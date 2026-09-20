import { NextResponse } from 'next/server';
import { encryptSecret, getRepoPublicKey, putRepoSecret } from '@/lib/github';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const code = searchParams.get('code');
  const error = searchParams.get('error');

  if (error) {
    return NextResponse.redirect(new URL(`/?error=${error}`, request.url));
  }

  if (!code) {
    return NextResponse.redirect(new URL(`/?error=no_code`, request.url));
  }

  const clientId = process.env.LINKEDIN_CLIENT_ID;
  const clientSecret = process.env.LINKEDIN_CLIENT_SECRET;
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || (process.env.VERCEL_PROJECT_PRODUCTION_URL ? `https://${process.env.VERCEL_PROJECT_PRODUCTION_URL}` : (process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : 'http://localhost:3000'));
  const redirectUri = `${siteUrl}/api/auth/callback`;
  
  const tokenRes = await fetch('https://www.linkedin.com/oauth/v2/accessToken', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      grant_type: 'authorization_code',
      code,
      redirect_uri: redirectUri,
      client_id: clientId!,
      client_secret: clientSecret!,
    }),
  });

  const tokenData = await tokenRes.json();
  if (!tokenRes.ok) {
    return NextResponse.redirect(new URL(`/?error=token_failed`, request.url));
  }
  
  const accessToken = tokenData.access_token;

  // Determine whether to post as Organization (Business Page) or Personal Profile
  let authorUrn = '';

  const configuredOrgId = process.env.LINKEDIN_ORGANIZATION_ID;
  if (configuredOrgId) {
    const cleanOrgId = configuredOrgId.replace(/[^0-9]/g, '');
    authorUrn = `urn:li:organization:${cleanOrgId}`;
  } else {
    // Try to auto-detect administered organization
    try {
      const orgRes = await fetch('https://api.linkedin.com/v2/organizationAcls?q=roleAssignee', {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (orgRes.ok) {
        const orgData = await orgRes.json();
        const orgElement = orgData?.elements?.find((el: any) => el?.state === 'APPROVED' && el?.organization);
        if (orgElement?.organization) {
          authorUrn = orgElement.organization;
        }
      }
    } catch (e) {
      console.warn('Could not auto-fetch organization ACLs:', e);
    }
  }

  // Fallback to personal profile if no organization found
  if (!authorUrn) {
    authorUrn = `urn:li:person:${userData.sub}`;
  }

  const githubPat = process.env.GITHUB_PAT;
  const repoOwner = process.env.GITHUB_REPO_OWNER || process.env.VERCEL_GIT_REPO_OWNER || 'Rushikeshkhadke';
  const repoName = process.env.GITHUB_REPO_NAME || process.env.VERCEL_GIT_REPO_SLUG || 'linkedin-quote-automation';


  if (!githubPat) {
    return NextResponse.redirect(new URL(`/?error=github_setup_missing`, request.url));
  }

  try {
    const { key_id, key } = await getRepoPublicKey(repoOwner, repoName, githubPat);
    
    const encryptedToken = await encryptSecret(accessToken, key);
    const encryptedUrn = await encryptSecret(authorUrn, key);

    await putRepoSecret(repoOwner, repoName, 'LINKEDIN_ACCESS_TOKEN', encryptedToken, key_id, githubPat);
    await putRepoSecret(repoOwner, repoName, 'LINKEDIN_AUTHOR_URN', encryptedUrn, key_id, githubPat);


    return NextResponse.redirect(new URL(`/?success=true`, request.url));
  } catch (err) {
    console.error(err);
    return NextResponse.redirect(new URL(`/?error=github_update_failed`, request.url));
  }
}
