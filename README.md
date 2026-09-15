# Daily LinkedIn Quote Automation

This repository contains an automated workflow that runs every day at 9:00 AM IST. It generates a unique quote using Gemini, creates an image using a Google Slides template, publishes it to LinkedIn, and logs the post in Google Sheets.

## Prerequisites

You will need to set up the following APIs and obtain their credentials:

1. **Google Cloud Console**:
   - Enable the **Google Sheets API**, **Google Slides API**, and **Google Drive API**.
   - Create a **Service Account** and download its JSON key file.
   - Share your Google Sheet and Google Slides template with the Service Account email address (give it Editor access).

2. **Gemini API**:
   - Get an API key from Google AI Studio.

3. **LinkedIn API**:
   - Create a LinkedIn App in the LinkedIn Developer Portal.
   - Request the "Share on LinkedIn" or "Sign In with LinkedIn" products to get the necessary scopes.
   - Generate an OAuth 2.0 Access Token with `w_member_social` permission.
   - Find your LinkedIn Author URN (it looks like `urn:li:person:YOUR_ID`).

## Setup in GitHub

1. Go to your repository on GitHub.
2. Navigate to **Settings** > **Secrets and variables** > **Actions**.
3. Create the following **New repository secrets**:
   - `GEMINI_API_KEY`: Your Gemini API key.
   - `GOOGLE_SERVICE_ACCOUNT_JSON`: The entire content of your Google Service Account JSON file.
   - `SPREADSHEET_ID`: The ID of your Google Sheet (found in its URL).
   - `LINKEDIN_ACCESS_TOKEN`: Your LinkedIn API access token.
   - `LINKEDIN_AUTHOR_URN`: Your LinkedIn URN (e.g., `urn:li:person:123456789`).

## How it works

The workflow uses **GitHub Actions** (`.github/workflows/publish_quote.yml`) to automatically run `main.py` at 3:30 AM UTC (which is 9:00 AM IST).

You can also run it manually from the "Actions" tab in GitHub by selecting the "Daily LinkedIn Quote Publisher" workflow and clicking "Run workflow".
