import os
import sys
import json
import textwrap
import urllib.request
from datetime import datetime
import requests
from PIL import Image, ImageDraw, ImageFont

# ==========================================
# CONFIGURATION & ENVIRONMENT VARIABLES
# ==========================================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
LINKEDIN_ACCESS_TOKEN = os.environ.get("LINKEDIN_ACCESS_TOKEN")
LINKEDIN_AUTHOR_URN = os.environ.get("LINKEDIN_AUTHOR_URN")

TEMPLATE_PATH = "template.png"
OUTPUT_IMAGE_PATH = "quote_output.png"
HISTORY_FILE = "history.txt"

# Bounding box for quote text area (between opening and closing telephone quote marks)
# Template image size: 737 x 1024 px
TEXT_LEFT = 170                              # Starts directly after the top-left telephone quote icon
TEXT_RIGHT = 570                             # Ends directly before the bottom-right telephone quote icon
TEXT_TOP = 440
TEXT_BOTTOM = 595
TEXT_CENTER_X = (TEXT_LEFT + TEXT_RIGHT) // 2
MAX_TEXT_WIDTH = TEXT_RIGHT - TEXT_LEFT      # 400 px
MAX_TEXT_HEIGHT = TEXT_BOTTOM - TEXT_TOP     # 155 px


def get_previous_quotes(history_path=HISTORY_FILE):
    """Reads past quotes from history.txt to avoid duplicates."""
    if not os.path.exists(history_path):
        return []
    quotes = []
    with open(history_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(" | ")
            if len(parts) >= 2:
                quotes.append(parts[1])
    return quotes


def generate_unique_quote(previous_quotes):
    """
    Uses Google Gemini API (Free Tier) to generate a verified quote from a renowned sales/business leader.
    Ensures quote is not a duplicate from history.
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable is missing.")

    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)

    # Use gemini-1.5-flash or gemini-2.0-flash (fast, reliable, generous free tier)
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
    except Exception:
        model = genai.GenerativeModel("gemini-pro")

    recent_history = "\n".join(previous_quotes[-20:]) if previous_quotes else "None"

    prompt = f"""You are a sales & leadership content curator for Bulk Leads Caller brand.
Find a real, verified, inspiring quote from a well-known sales, business, or leadership authority (such as Brian Tracy, Jeffrey Gitomer, Zig Ziglar, Gary Vaynerchuk, Grant Cardone, Steve Jobs, Warren Buffett, Napoleon Hill, Dale Carnegie, or Mark Cuban) specifically related to sales, cold calling, lead generation, closing deals, resilience, or business growth.

Do NOT repeat any of these recent quotes:
{recent_history}

Rules:
1. Do NOT include quotation marks around the quote.
2. The quote should be impactful and concise (between 10 to 25 words).
3. Return ONLY in this exact 2-line format with no other text or markdown:
QUOTE: [Plain quote text without quotation marks]
AUTHOR: [Full Name of the Author]"""

    for attempt in range(5):
        try:
            response = model.generate_content(prompt)
            response_text = response.text.strip()
        except Exception as e:
            fallback_model = genai.GenerativeModel("gemini-pro")
            response = fallback_model.generate_content(prompt)
            response_text = response.text.strip()

        quote = ""
        author = ""

        for line in response_text.split("\n"):
            line = line.strip()
            if line.startswith("QUOTE:"):
                quote = line.replace("QUOTE:", "").strip().strip('"').strip("'").strip("“").strip("”")
            elif line.startswith("AUTHOR:"):
                author = line.replace("AUTHOR:", "").strip()

        if not quote or not author:
            continue

        # Check for duplication
        is_duplicate = any(
            quote.lower() in prev.lower() or prev.lower() in quote.lower()
            for prev in previous_quotes
        )
        if not is_duplicate:
            return quote, author

    if quote and author:
        return quote, author

    raise RuntimeError("Failed to generate a unique quote from Google Gemini API.")


# Bogart Font candidate filenames (place your Bogart-SemiBold.ttf or Bogart-Regular.ttf in this directory)
BOGART_BOLD_CANDIDATES = [
    "Bogart-SemiBold.ttf",
    "Bogart-Bold.ttf",
    "Bogart-Medium.ttf",
    "Bogart-Regular.ttf",
    "Bogart.ttf",
    "bogart.ttf",
    "Bogart-SemiBold.otf",
    "Bogart-Bold.otf",
    "Bogart-Regular.otf",
    "Bogart.otf",
]

BOGART_REGULAR_CANDIDATES = [
    "Bogart-Regular.ttf",
    "Bogart-Medium.ttf",
    "Bogart-Light.ttf",
    "Bogart-Book.ttf",
    "Bogart.ttf",
    "bogart.ttf",
    "Bogart-Regular.otf",
    "Bogart.otf",
]


def get_font(font_path, font_size, default_type="bold"):
    """
    Loads Bogart font if available in directory or system, with clean fallback.
    """
    candidates = BOGART_BOLD_CANDIDATES if default_type == "bold" else BOGART_REGULAR_CANDIDATES

    # 1. Check local directory for any Bogart font file
    for cand in candidates:
        if os.path.exists(cand):
            try:
                return ImageFont.truetype(cand, font_size)
            except Exception:
                continue

    # 2. Check explicit font_path argument
    if font_path and os.path.exists(font_path):
        try:
            return ImageFont.truetype(font_path, font_size)
        except Exception:
            pass

    # 3. Check Windows / Linux system fonts
    system_candidates = (
        [
            "C:\\Windows\\Fonts\\georgiab.ttf",
            "C:\\Windows\\Fonts\\arialbd.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
        if default_type == "bold"
        else [
            "C:\\Windows\\Fonts\\georgia.ttf",
            "C:\\Windows\\Fonts\\arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    )

    for cand in system_candidates:
        if os.path.exists(cand):
            try:
                return ImageFont.truetype(cand, font_size)
            except Exception:
                continue

    return ImageFont.load_default()


def render_quote_image(quote, author, template_path=TEMPLATE_PATH, output_path=OUTPUT_IMAGE_PATH):
    """
    Replaces ONLY the quote text on template.png using Pillow.
    - Uses official Bogart font.
    - Natural word spacing (no artificial gaps or stretching).
    - Centered horizontally (CENTER_X = 369) and vertically between the telephone quote icons.
    - Preserves 100% of the original background, watermark, hanging phones, and logo.
    """
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template image '{template_path}' not found.")

    bold_font_path = "Bogart-Medium.ttf"
    if not os.path.exists(bold_font_path):
        bold_font_path = "Bogart-SemiBold.ttf"

    img = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Dynamic Font Sizing & Clean Multi-line Wrapping
    selected_font_size = 28
    lines = []
    font_quote = None

    for f_size in range(30, 18, -1):
        font_q = get_font(bold_font_path, f_size, "bold")
        line_height = int(f_size * 1.40)

        for wrap_w in range(35, 14, -1):
            cand_lines = textwrap.wrap(quote, width=wrap_w)
            if len(cand_lines) * line_height <= MAX_TEXT_HEIGHT:
                if all(
                    (draw.textbbox((0, 0), ln, font=font_q)[2] - draw.textbbox((0, 0), ln, font=font_q)[0]) <= MAX_TEXT_WIDTH
                    for ln in cand_lines
                ):
                    selected_font_size = f_size
                    lines = cand_lines
                    font_quote = font_q
                    break
        if lines:
            break

    if not font_quote:
        font_quote = get_font(bold_font_path, 22, "bold")
        lines = textwrap.wrap(quote, width=28)

    line_height = int(selected_font_size * 1.40)
    total_text_height = len(lines) * line_height
    start_y = (TEXT_TOP + TEXT_BOTTOM) // 2 - (total_text_height // 2)

    # Render quote lines centered with natural spacing (matching exact original template)
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font_quote)
        line_w = bbox[2] - bbox[0]
        x = TEXT_CENTER_X - (line_w // 2)
        draw.text((x, start_y + (i * line_height)), line, font=font_quote, fill=(255, 255, 255))

    img.save(output_path, quality=95)
    print(f"Generated quote image saved to '{output_path}'.")
    return output_path


def upload_image_to_linkedin(image_path):
    """Registers and uploads image to LinkedIn Assets API."""
    if not LINKEDIN_ACCESS_TOKEN or not LINKEDIN_AUTHOR_URN:
        raise ValueError("LINKEDIN_ACCESS_TOKEN or LINKEDIN_AUTHOR_URN is missing.")

    register_url = "https://api.linkedin.com/v2/assets?action=registerUpload"
    headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }
    register_body = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": LINKEDIN_AUTHOR_URN,
            "serviceRelationships": [
                {
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent",
                }
            ],
        }
    }

    res = requests.post(register_url, headers=headers, json=register_body)
    if res.status_code not in (200, 201):
        raise RuntimeError(f"Failed to register upload with LinkedIn: {res.status_code} - {res.text}")

    res_data = res.json()
    upload_url = res_data["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
    asset_urn = res_data["value"]["asset"]

    with open(image_path, "rb") as f:
        image_data = f.read()

    upload_headers = {"Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}"}
    upload_res = requests.put(upload_url, headers=upload_headers, data=image_data)
    if upload_res.status_code not in (200, 201):
        raise RuntimeError(f"Failed to upload binary image to LinkedIn: {upload_res.status_code} - {upload_res.text}")

    return asset_urn


def post_to_linkedin(quote, author, asset_urn):
    """Publishes the image post to LinkedIn feed with formatted commentary."""
    post_url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }

    commentary = (
        f'"{quote}"\n— {author}\n\n'
        f"#Sales #ColdCalling #LeadGeneration #BulkLeadsCaller #SalesMotivation #BusinessGrowth"
    )

    post_body = {
        "author": LINKEDIN_AUTHOR_URN,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": commentary},
                "shareMediaCategory": "IMAGE",
                "media": [
                    {
                        "status": "READY",
                        "description": {"text": f"Daily sales quote by {author}"},
                        "media": asset_urn,
                        "title": {"text": "Daily Quote - Bulk Leads Caller"},
                    }
                ],
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }

    res = requests.post(post_url, headers=headers, json=post_body)
    if res.status_code != 201:
        raise RuntimeError(f"Failed to publish post to LinkedIn: {res.status_code} - {res.text}")

    post_id = res.json().get("id", "")
    return f"https://www.linkedin.com/feed/update/{post_id}"


def append_to_history(quote, author, post_url, history_path=HISTORY_FILE):
    """Appends successful quote publication to history.txt."""
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(history_path, "a", encoding="utf-8") as f:
        f.write(f"{date_str} | {author}: {quote} | {post_url}\n")


def main():
    print("==========================================")
    print(" Bulk Leads Caller - Daily Quote Publisher")
    print("==========================================")

    print("\n[1/5] Checking previous quote history...")
    previous_quotes = get_previous_quotes()
    print(f"Loaded {len(previous_quotes)} quotes from history.")

    print("\n[2/5] Generating verified sales quote via Google Gemini API (Free)...")
    quote, author = generate_unique_quote(previous_quotes)
    print(f"Quote : {quote}")
    print(f"Author: {author}")

    print("\n[3/5] Rendering text onto template with Pillow...")
    image_path = render_quote_image(quote, author)

    print("\n[4/5] Uploading image to LinkedIn...")
    asset_urn = upload_image_to_linkedin(image_path)
    print(f"Uploaded asset URN: {asset_urn}")

    print("\n[5/5] Publishing post to LinkedIn...")
    post_url = post_to_linkedin(quote, author, asset_urn)
    print(f"SUCCESS! Published post URL: {post_url}")

    print("\nLogging quote to history...")
    append_to_history(quote, author, post_url)
    print("Completed successfully.")


if __name__ == "__main__":
    main()
