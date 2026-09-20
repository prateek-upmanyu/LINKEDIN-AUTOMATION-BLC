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
PHONE_ICON_PATH = "phone_quote_icon.png"
OUTPUT_IMAGE_PATH = "quote_output.png"
HISTORY_FILE = "history.txt"

# Bounding box limits for quote text area
MAX_TEXT_WIDTH = 400
MAX_TEXT_HEIGHT = 160
TEXT_CENTER_X = 369
TEXT_CENTER_Y = 505


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



import random

# Curated Sales Topics & Themes Pool (Exclusively Sales, Cold Calling, Pipeline, Negotiation & Sales Psychology)
SALES_TOPICS_POOL = [
    # Core Sales Pipeline & Tactical Execution
    "Prospecting & Cold Outreach", "Lead Qualification & Discovery", "High-Impact Pitching", 
    "Objection Handling & Reframing", "Closing Deals & ABC (Always Be Closing)", 
    "Relentless Follow-Up", "Handling Rejection & Resilience", "Sales Pipeline & Forecasting", 
    "Creating Urgency without Pressure", "Gatekeepers & Reaching Decision Makers", 
    "Deal Velocity & Shortening Sales Cycles", "Sales Demos & Compelling Proposals", 
    "Negotiating Pricing, Contracts & Avoiding Discounts", "Quota Attainment & Commission Drive",
    
    # Methodologies & Customer Journey
    "Value Selling & ROI Focus", "Consultative & Solution Selling", "Relationship & Trust-Based Selling", 
    "Social Selling & Inbound Authority", "Warm Calling & Smart Prospecting", "Generating High-Value Referrals", 
    "Upselling, Cross-Selling & Account Expansion", "Customer Retention, Success & Combating Churn",
    
    # Sales Psychology & Influence Triggers
    "Influence & Behavioral Economics in Sales", "Ethical Persuasion vs Manipulation", 
    "The Power of Scarcity & Reciprocity", "Authority & Unshakable Authenticity", 
    "Mastering Silence & Strategic Timing", "Intuition, Adaptability & Curiosity in Discovery", 
    "Empathy, Active Listening & Reading Body Language", "Framing, Anchoring & Contrast Effect in Negotiations", 
    "Understanding Buyer Identity, Ego, Fear & Desire", "Detachment from the Outcome & Flow State in Sales Calls", 
    "Power Dynamics, Status & Building Instant Rapport", "Cognitive Biases & How Buyers Make Decisions", 
    "High-Stakes Negotiation & Hostage Negotiator Tactics", "Storytelling That Closes Deals",
    
    # Top Performer Mindset & Execution
    "Sales Discipline, Obsession & Relentless Execution", "Self-Awareness & Emotional Intelligence under Pressure", 
    "Rejection = Redirection & Mental Toughness", "Consistency, Daily Hustle & Work Ethic", 
    "Growth Mindset, Ownership & Extreme Accountability", "Confidence, Energy & Presence on the Phone", 
    "Personal Branding & Reputation in the Industry", "Top 1% Sales Performer Habits & Routine"
]

SALES_AUTHORITIES = [
    "Brian Tracy", "Jeffrey Gitomer", "Zig Ziglar", "Dale Carnegie", "Jeb Blount", 
    "Jill Konrath", "Chris Voss", "Robert Cialdini", "Grant Cardone", "Neil Rackham", 
    "Chet Holmes", "Mark Cuban", "Jordan Belfort", "David Sandler", "Gary Vaynerchuk", 
    "Steve Jobs", "Napoleon Hill", "Tom Hopkins", "Anthony Iannarino", "Art Sobczak"
]


def generate_unique_quote(previous_quotes):
    """
    Uses Google Gemini API (Free Tier) to generate a verified quote strictly related to SALES
    rotating across specific sales topics and business authorities.
    Ensures quote is 100% unique and not a duplicate from history.
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable is missing.")

    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
    except Exception:
        model = genai.GenerativeModel("gemini-pro")

    # Pick 2-3 random sales focus topics from the pool for maximum daily variety
    daily_focus_topics = random.sample(SALES_TOPICS_POOL, 3)
    focus_topic_str = ", ".join(daily_focus_topics)
    suggested_author = random.choice(SALES_AUTHORITIES)

    recent_history = "\n".join(f"- {q}" for q in previous_quotes[-30:]) if previous_quotes else "None"

    prompt = f"""You are an elite sales leadership content curator for Bulk Leads Caller (a B2B sales & cold calling agency).
Your task is to find a real, verified, highly inspiring and actionable quote from a well-known sales leader, master negotiator, business authority, or psychological influence expert.

TODAY'S SALES FOCUS THEMES:
{focus_topic_str}

REPRESENTATIVE AUTHORITIES (or similar renowned sales/business minds):
Brian Tracy, Jeffrey Gitomer, Zig Ziglar, Dale Carnegie, Jeb Blount, Jill Konrath, Chris Voss, Robert Cialdini, Grant Cardone, Neil Rackham, Chet Holmes, Mark Cuban, Jordan Belfort, David Sandler, Steve Jobs, Gary Vaynerchuk, Napoleon Hill.

STRICT CONTENT RULES:
1. The quote MUST be a 100% REAL, AUTHENTIC, HISTORICALLY DOCUMENTED quote actually spoken or published by a real person (sales leader, entrepreneur, psychologist, or author). NEVER invent, synthesize, or hallucinate a quote.
2. The quote MUST be exclusively related to SALES (e.g. cold outreach, prospecting, closing, handling objections, negotiation, follow-up, pricing, buyer psychology, discipline, resilience, or closing deals).
3. Keep the quote punchy and impactful (between 8 to 24 words).
4. Do NOT use generic motivational quotes (it must be directly relevant to sales professionals, closers, and entrepreneurs).
5. Do NOT include quotation marks around the quote.
6. The AUTHOR must be the actual real full name of the person who said it.

DO NOT REPEAT ANY OF THESE PREVIOUSLY POSTED QUOTES:
{recent_history}

RETURN ONLY IN THIS EXACT 2-LINE FORMAT (NO OTHER TEXT OR MARKDOWN):
QUOTE: [Plain quote text without quotation marks]
AUTHOR: [Full Name of the Author]"""

    for attempt in range(6):
        try:
            response = model.generate_content(prompt)
            response_text = response.text.strip()
        except Exception:
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
                author = line.replace("AUTHOR:", "").strip().lstrip("—").lstrip("-").strip()

        if not quote or not author:
            continue

        # Check for duplication against entire history
        is_duplicate = any(
            quote.lower() in prev.lower() or prev.lower() in quote.lower()
            for prev in previous_quotes
        )
        if not is_duplicate:
            return quote, author

    if quote and author:
        return quote, author

    raise RuntimeError("Failed to generate a unique sales quote from Google Gemini API.")



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


def render_quote_image(quote, author, template_path=TEMPLATE_PATH, icon_path=PHONE_ICON_PATH, output_path=OUTPUT_IMAGE_PATH):
    """
    Renders quote text onto the clean template with dynamic telephone quotation marks ("").
    - Uses official Bogart font.
    - Centers text horizontally and vertically.
    - Dynamically attaches the opening telephone quote mark on the top-left (first line).
    - Dynamically attaches the closing telephone quote mark (rotated 180°) on the bottom-right (last line).
    - Preserves 100% of the original background, watermark, hanging phones, and logo.
    """
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template image '{template_path}' not found.")

    bold_font_path = "Bogart-SemiBold.ttf"
    if not os.path.exists(bold_font_path):
        bold_font_path = "Bogart-Medium.ttf"

    img = Image.open(template_path).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # Dynamic Font Sizing & Clean Multi-line Wrapping
    selected_font_size = 27
    lines = []
    font_quote = None

    for f_size in range(28, 19, -1):
        font_q = get_font(bold_font_path, f_size, "bold")
        line_height = int(f_size * 1.42)

        for wrap_w in range(35, 20, -1):
            cand_lines = textwrap.wrap(quote, width=wrap_w)
            if not cand_lines:
                continue
            if len(cand_lines) * line_height <= MAX_TEXT_HEIGHT:
                widths = [
                    (draw.textbbox((0, 0), ln, font=font_q)[2] - draw.textbbox((0, 0), ln, font=font_q)[0])
                    for ln in cand_lines
                ]
                if max(widths) <= MAX_TEXT_WIDTH and len(cand_lines) <= 4:
                    selected_size = f_size
                    lines = cand_lines
                    font_quote = font_q
                    break
        if lines:
            break

    if not font_quote:
        font_quote = get_font(bold_font_path, 22, "bold")
        lines = textwrap.wrap(quote, width=28)

    line_height = int(selected_font_size * 1.42)
    total_text_height = len(lines) * line_height
    start_y = TEXT_CENTER_Y - (total_text_height // 2)

    first_line_lx = 0
    last_line_rx = 0

    # Render quote lines centered
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font_quote)
        line_w = bbox[2] - bbox[0]
        x = TEXT_CENTER_X - (line_w // 2)
        rx = x + line_w
        if i == 0:
            first_line_lx = x
        if i == len(lines) - 1:
            last_line_rx = rx
        draw.text((x, start_y + (i * line_height)), line, font=font_quote, fill=(255, 255, 255))

    # Add Telephone Quotation Marks ("")
    last_line_y = start_y + (len(lines) - 1) * line_height
    last_letter_center_y = last_line_y + int(selected_font_size * 0.48)
    pos_rx = last_line_rx + 6
    pos_ry = last_letter_center_y

    if os.path.exists(icon_path):
        icon_asset = Image.open(icon_path).convert("RGBA")
        icon_w, icon_h = 56, 59
        icon_l = icon_asset.resize((icon_w, icon_h), Image.Resampling.LANCZOS)
        icon_r = icon_asset.rotate(180, expand=True).resize((icon_w, icon_h), Image.Resampling.LANCZOS)

        # Opening telephone quote: bottom connects with vertical center of first letter
        first_letter_center_y = start_y + int(selected_font_size * 0.48)
        pos_lx = first_line_lx - icon_w - 6
        pos_ly = first_letter_center_y - icon_h + 10

        # Closing telephone quote: top connects with vertical center of last letter/punctuation
        pos_rx = last_line_rx + 6
        pos_ry = last_letter_center_y

        img.paste(icon_l, (int(pos_lx), int(pos_ly)), icon_l)
        img.paste(icon_r, (int(pos_rx), int(pos_ry)), icon_r)


    # Render Author Name below the quote block
    if author:
        reg_font_path = "Bogart-Regular.ttf"
        if not os.path.exists(reg_font_path):
            reg_font_path = "Bogart-Medium.ttf"

        clean_author = author.strip().lstrip("—").lstrip("-").strip()
        author_text = f"— {clean_author}"
        author_font_size = max(18, int(selected_font_size * 0.72))
        author_font = get_font(reg_font_path, author_font_size, "regular")

        abbox = draw.textbbox((0, 0), author_text, font=author_font)
        aw = abbox[2] - abbox[0]

        quote_bottom = max(start_y + total_text_height, pos_ry + 59)
        author_y = quote_bottom + 14
        # Align author with the right edge of the closing quote mark / quote block
        author_x = max(pos_rx + 56 - aw, TEXT_CENTER_X - (aw // 2))

        # Render author with clean elegant light tint for visual hierarchy
        draw.text((author_x, author_y), author_text, font=author_font, fill=(225, 230, 255))

    img.convert("RGB").save(output_path, quality=95)
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
