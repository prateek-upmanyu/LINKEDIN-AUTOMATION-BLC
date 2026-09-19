# 📞 Bulk Leads Caller — LinkedIn Daily Quote Automation

Automated daily quote publisher for the **Bulk Leads Caller** brand page on LinkedIn. Every day at **9:00 AM IST**, this system generates a verified sales/lead generation quote using the **Google Gemini API (100% Free)**, renders it directly onto the branded template image using Pillow (without altering background, logo, or quote decorations), and publishes it to LinkedIn.

---

## 🎨 Template Design & Text Placement Analysis

The template image (`template.png`) has dimensions **737 × 1024 px** with a dark navy background (`#212254`) and a diagonal watermark phone receiver.

### 📍 Text Area Mapping:
* **Opening Quote Mark (Telephone Icon):** Located at Top-Left (`x: 114–165`, `y: 437–492`).
* **Closing Quote Mark (Telephone Icon):** Located at Bottom-Right (`x: 574–627`, `y: 545–601`).
* **Quote Text Zone:**
  * **Horizontal Bounds:** `x: 175` to `x: 565` (Width = 390 px, Center X = 370 px)
  * **Vertical Bounds:** `y: 438` to `y: 598` (Height = 160 px, Center Y = 518 px)
  * **Alignment:** Centered horizontally and vertically in this zone.
  * **Note:** **NO quotation marks (`" "` or `' '`)** are added around the quote text by Pillow because the telephone icons are baked into the template as the quote marks.
* **Author Placement:**
  * **Position:** Bottom-right corner below the quote area (`x: Right-aligned to 565`, `y: 612–620`).
  * **Format:** `— Author Name` (e.g. `— Brian Tracy`).
  * **Font:** Medium/regular weight in a soft white tint (`#CDD7FF`).

---

## 🚀 Tech Stack

* **Python 3.10+ / 3.11**
* **Google Gemini API (`gemini-1.5-flash`):** 100% Free tier, high reliability for sales quote generation.
* **Pillow (`PIL`):** Dynamic multi-line wrapping, auto font-scaling, and crisp text rendering.
* **LinkedIn UGC Posts API:** Multi-step image asset registration, binary upload, and public post publishing.
* **GitHub Actions:** Automated cron schedule (`30 3 * * *` = 9:00 AM IST) and manual triggers (`workflow_dispatch`).

---

## ⚙️ Setup & Configuration

### 1. Required GitHub Secrets

Add the following 3 secrets to your GitHub repository (**Settings > Secrets and variables > Actions > New repository secret**):

| Secret Name | Description | Example |
|---|---|---|
| `GEMINI_API_KEY` | Free Google Gemini API Key from Google AI Studio | `AIzaSy...` |
| `LINKEDIN_ACCESS_TOKEN` | OAuth 2.0 Access Token with posting permissions | `AQV...` |
| `LINKEDIN_AUTHOR_URN` | URN of the Author (Person or Organization Page) | `urn:li:organization:12345678` or `urn:li:person:abcdef12` |

---

### 2. Local Testing

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file (see `.env.example`) or export environment variables:
```bash
export GEMINI_API_KEY="your-gemini-api-key"
export LINKEDIN_ACCESS_TOKEN="your-linkedin-token"
export LINKEDIN_AUTHOR_URN="urn:li:organization:your-org-id"
```

3. Run the script:
```bash
python main.py
```

4. The script will generate `quote_output.png`, upload it to LinkedIn, post to the feed, and log the quote to `history.txt`.

---

## ⏰ Schedule Details

The automation runs automatically via GitHub Actions:
* **Schedule:** `cron: '30 3 * * *'` (3:30 AM UTC = **9:00 AM IST** every day).
* **Manual Trigger:** Go to **GitHub > Actions > Daily LinkedIn Quote Automation > Run workflow** to test anytime on demand.
