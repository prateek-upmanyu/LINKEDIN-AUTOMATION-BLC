import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const { time } = await request.json(); // Format: "HH:MM" in 24hr IST (e.g. "09:00")
    if (!time) {
      return NextResponse.json({ error: 'Time is required' }, { status: 400 });
    }

    // Convert IST to UTC for cron
    // IST is UTC + 5:30. So UTC = IST - 5:30
    const [hoursStr, minutesStr] = time.split(':');
    let hours = parseInt(hoursStr, 10);
    let minutes = parseInt(minutesStr, 10);

    minutes -= 30;
    if (minutes < 0) {
      minutes += 60;
      hours -= 1;
    }
    hours -= 5;
    if (hours < 0) {
      hours += 24;
    }

    const cron = `${minutes} ${hours} * * *`;

    const githubPat = process.env.GITHUB_PAT;
    const repoOwner = process.env.GITHUB_REPO_OWNER || 'Rushikeshkhadke';
    const repoName = process.env.GITHUB_REPO_NAME || 'linkedin-quote-automation';
    const path = '.github/workflows/publish_quote.yml';

    if (!githubPat) {
      return NextResponse.json({ error: 'GITHUB_PAT missing' }, { status: 500 });
    }

    // 1. Get current file (to get SHA)
    const getRes = await fetch(`https://api.github.com/repos/${repoOwner}/${repoName}/contents/${path}`, {
      headers: {
        Authorization: `token ${githubPat}`,
        Accept: 'application/vnd.github.v3+json',
      }
    });

    if (!getRes.ok) {
      return NextResponse.json({ error: 'Failed to fetch workflow file' }, { status: 500 });
    }

    const fileData = await getRes.json();
    const sha = fileData.sha;
    
    // Decode base64 content
    const contentStr = Buffer.from(fileData.content, 'base64').toString('utf8');
    
    // Replace cron
    const newContentStr = contentStr.replace(/cron:\s*'.*?'/, `cron: '${cron}'`);
    const newBase64Content = Buffer.from(newContentStr, 'utf8').toString('base64');

    // 2. Update file
    const updateRes = await fetch(`https://api.github.com/repos/${repoOwner}/${repoName}/contents/${path}`, {
      method: 'PUT',
      headers: {
        Authorization: `token ${githubPat}`,
        Accept: 'application/vnd.github.v3+json',
      },
      body: JSON.stringify({
        message: `Update post time to ${time} IST`,
        content: newBase64Content,
        sha: sha
      })
    });

    if (!updateRes.ok) {
      const errText = await updateRes.text();
      return NextResponse.json({ error: `Failed to update file: ${errText}` }, { status: 500 });
    }

    return NextResponse.json({ success: true, cron });
  } catch (err) {
    console.error(err);
    return NextResponse.json({ error: 'Server error' }, { status: 500 });
  }
}
