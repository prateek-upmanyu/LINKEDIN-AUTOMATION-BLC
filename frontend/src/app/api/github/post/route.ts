import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const githubPat = process.env.GITHUB_PAT;
    const repoOwner = process.env.GITHUB_REPO_OWNER || process.env.VERCEL_GIT_REPO_OWNER || 'prateek-upmanyu';
    const repoName = process.env.GITHUB_REPO_NAME || process.env.VERCEL_GIT_REPO_SLUG || 'LINKEDIN-AUTOMATION-BLC';
    const workflowId = 'daily_post.yml';

    if (!githubPat) {
      return NextResponse.json({ error: 'GITHUB_PAT missing' }, { status: 500 });
    }

    const triggerRes = await fetch(`https://api.github.com/repos/${repoOwner}/${repoName}/actions/workflows/${workflowId}/dispatches`, {
      method: 'POST',
      headers: {
        Authorization: `token ${githubPat}`,
        Accept: 'application/vnd.github.v3+json',
      },
      body: JSON.stringify({
        ref: 'master'
      })
    });

    if (!triggerRes.ok) {
      const errText = await triggerRes.text();
      return NextResponse.json({ error: `Failed to trigger post: ${errText}` }, { status: 500 });
    }

    return NextResponse.json({ success: true });
  } catch (err) {
    console.error(err);
    return NextResponse.json({ error: 'Server error' }, { status: 500 });
  }
}
