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
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000';
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

  const userRes = await fetch('https://api.linkedin.com/v2/userinfo', {
    headers: { Authorization: `Bearer ${accessToken}` },
  });

  const userData = await userRes.json();
  if (!userRes.ok) {
    return NextResponse.redirect(new URL(`/?error=user_failed`, request.url));
  }
  
  const urn = `urn:li:person:${userData.sub}`;

  const githubPat = process.env.GITHUB_PAT;
  const repoOwner = process.env.GITHUB_REPO_OWNER || 'Rushikeshkhadke';
  const repoName = process.env.GITHUB_REPO_NAME || 'linkedin-quote-automation';

  if (!githubPat) {
    return NextResponse.redirect(new URL(`/?error=github_setup_missing`, request.url));
  }

  try {
    const { key_id, key } = await getRepoPublicKey(repoOwner, repoName, githubPat);
    
    const encryptedToken = await encryptSecret(accessToken, key);
    const encryptedUrn = await encryptSecret(urn, key);

    await putRepoSecret(repoOwner, repoName, 'LINKEDIN_ACCESS_TOKEN', encryptedToken, key_id, githubPat);
    await putRepoSecret(repoOwner, repoName, 'LINKEDIN_AUTHOR_URN', encryptedUrn, key_id, githubPat);

    return NextResponse.redirect(new URL(`/?success=true`, request.url));
  } catch (err) {
    console.error(err);
    return NextResponse.redirect(new URL(`/?error=github_update_failed`, request.url));
  }
}
