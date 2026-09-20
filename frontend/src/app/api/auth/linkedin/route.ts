import { NextResponse } from 'next/server';

export async function GET() {
  const clientId = process.env.LINKEDIN_CLIENT_ID;
  
  if (!clientId) {
    return NextResponse.json({ error: 'LINKEDIN_CLIENT_ID is not configured' }, { status: 500 });
  }

  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || (process.env.VERCEL_PROJECT_PRODUCTION_URL ? `https://${process.env.VERCEL_PROJECT_PRODUCTION_URL}` : (process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : 'http://localhost:3000'));
  const redirectUri = `${siteUrl}/api/auth/callback`;
  
  // modern scopes supporting both Personal profile & Company/Business organization pages
  const scope = 'w_member_social w_organization_social r_organization_social profile email openid';
  const state = Math.random().toString(36).substring(7);
  
  const authUrl = `https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=${clientId}&redirect_uri=${encodeURIComponent(redirectUri)}&state=${state}&scope=${encodeURIComponent(scope)}`;
  
  return NextResponse.redirect(authUrl);
}
