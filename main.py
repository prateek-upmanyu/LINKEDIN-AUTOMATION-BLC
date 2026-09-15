import os
from datetime import datetime
import requests
import google.generativeai as genai

# Environment Variables
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
LINKEDIN_ACCESS_TOKEN = os.environ.get("LINKEDIN_ACCESS_TOKEN")
LINKEDIN_AUTHOR_URN = os.environ.get("LINKEDIN_AUTHOR_URN")

def get_previous_quotes():
    if not os.path.exists('history.txt'):
        return []
    with open('history.txt', 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def generate_unique_quote(previous_quotes):
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')

    prompt = """Find a real, famous quote from a well-known person (like Grant Cardone, Steve Jobs, Zig Ziglar, Brian Tracy, Jeffrey Gitomer, Gary Vaynerchuk, Warren Buffett, Napoleon Hill, or other famous sales/business leaders) related to sales, cold calling, lead generation, or business success.

Return ONLY in this exact format (two lines, nothing else):
QUOTE: [the quote text here]
AUTHOR: [Full Name]"""

    for _ in range(5):
        response = model.generate_content(prompt)
        text = response.text.strip()

        quote = ""
        author = ""
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('QUOTE:'):
                quote = line.replace('QUOTE:', '').strip().strip('"').strip("'")
            elif line.startswith('AUTHOR:'):
                author = line.replace('AUTHOR:', '').strip()

        if not quote or not author:
            continue

        is_duplicate = any(
            quote.lower() in prev.lower() or prev.lower() in quote.lower()
            for prev in previous_quotes
        )
        if not is_duplicate:
            return quote, author

    raise Exception("Failed to generate a unique quote after 5 attempts.")

def create_local_image(quote, author):
    from PIL import Image, ImageDraw, ImageFont
    import textwrap
    import urllib.request
    import os

    template_path = 'template.png'
    output_path = 'quote.png'

    if not os.path.exists(template_path):
        raise Exception(f"Template image {template_path} not found.")

    img = Image.open(template_path).convert('RGB')
    draw = ImageDraw.Draw(img)

    # Download fonts if not present
    bold_path = 'Roboto-Bold.ttf'
    regular_path = 'Roboto-Regular.ttf'
    if not os.path.exists(bold_path):
        try:
            urllib.request.urlretrieve("https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Bold.ttf", bold_path)
        except Exception:
            pass

    if not os.path.exists(regular_path):
        try:
            urllib.request.urlretrieve("https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Regular.ttf", regular_path)
        except Exception:
            pass

    # HARD boundaries - text NEVER crosses these
    L   = 175  # left boundary
    R   = 565  # right boundary
    TOP = 440  # top boundary
    BOT = 598  # bottom boundary
    CX  = (L + R) // 2
    MAX_W = R - L
    MAX_H = BOT - TOP

    # Try font sizes from large to small until everything fits
    font_size = 38
    lines = []
    font_q = None

    for f_size in range(38, 16, -1):
        try:
            font_q = ImageFont.truetype(bold_path, f_size)
        except Exception:
            try:
                font_q = ImageFont.truetype('C:\\Windows\\Fonts\\arialbd.ttf', f_size)
            except Exception:
                font_q = ImageFont.load_default()

        LINE_H = int(f_size * 1.35)

        # Find max chars_per_line that doesn't exceed MAX_W
        cpw = 40
        for w in range(40, 3, -1):
            raw = textwrap.wrap(quote, width=w)
            # Check pixel width of each line
            if all(draw.textbbox((0,0), ln, font=font_q)[2] - draw.textbbox((0,0), ln, font=font_q)[0] <= MAX_W for ln in raw):
                cpw = w
                break
        
        lines = textwrap.wrap(quote, width=cpw)

        # Check total height fits
        if len(lines) * LINE_H <= MAX_H:
            font_size = f_size
            break

    # Draw centered in zone
    y0 = (TOP + BOT) // 2 - (len(lines) * LINE_H) // 2
    for i, line in enumerate(lines):
        bb = draw.textbbox((0,0), line, font=font_q)
        lw = bb[2] - bb[0]
        x  = CX - lw // 2
        # Safety clamp
        x  = max(L, min(x, R - lw))
        draw.text((x, y0 + i*LINE_H), line, font=font_q, fill=(255,255,255))

    # Author: below right icon, right-aligned, never outside R
    try:
        font_a = ImageFont.truetype(regular_path, 20)
    except Exception:
        try:
            font_a = ImageFont.truetype('C:\\Windows\\Fonts\\arial.ttf', 20)
        except Exception:
            font_a = font_q

    aline = f"— {author}"
    bb = draw.textbbox((0,0), aline, font=font_a)
    aw = bb[2] - bb[0]
    draw.text((R - aw, BOT + 10), aline, font=font_a, fill=(200,200,255))

    img.save(output_path)
    return output_path

def upload_image_to_linkedin(image_path):
    register_url = "https://api.linkedin.com/v2/assets?action=registerUpload"
    headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    register_body = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": LINKEDIN_AUTHOR_URN,
            "serviceRelationships": [{
                "relationshipType": "OWNER",
                "identifier": "urn:li:userGeneratedContent"
            }]
        }
    }
    res      = requests.post(register_url, headers=headers, json=register_body)
    res_data = res.json()
    upload_url = res_data['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
    asset_urn  = res_data['value']['asset']

    with open(image_path, 'rb') as f:
        image_data = f.read()

    upload_headers = {"Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}"}
    upload_res = requests.put(upload_url, headers=upload_headers, data=image_data)
    if upload_res.status_code not in (200, 201):
        raise Exception(f"Failed to upload image to LinkedIn: {upload_res.text}")

    return asset_urn

def post_to_linkedin(quote, author, asset_urn):
    post_url = "https://api.linkedin.com/v2/ugcPosts"
    headers  = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    caption = f'"{quote}"\n— {author}\n\n#Motivation #Sales #BulkLeadsCaller #ColdCalling #LeadGeneration'
    post_body = {
        "author": LINKEDIN_AUTHOR_URN,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": caption},
                "shareMediaCategory": "IMAGE",
                "media": [{
                    "status": "READY",
                    "description": {"text": "Daily Quote"},
                    "media": asset_urn,
                    "title": {"text": "Daily Quote"}
                }]
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    res = requests.post(post_url, headers=headers, json=post_body)
    if res.status_code != 201:
        raise Exception(f"Failed to post to LinkedIn: {res.text}")

    post_id = res.json().get('id', '')
    return f"https://www.linkedin.com/feed/update/{post_id}"

def append_to_history(quote, author, post_url):
    date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open('history.txt', 'a', encoding='utf-8') as f:
        f.write(f"{date_str} | {author}: {quote} | {post_url}\n")

def main():
    print("Starting Daily LinkedIn Quote Publisher...")

    print("Fetching previous quotes...")
    previous_quotes = get_previous_quotes()

    print("Generating famous quote...")
    quote, author = generate_unique_quote(previous_quotes)
    print(f"Quote  : {quote}")
    print(f"Author : {author}")

    print("Creating quote image...")
    image_path = create_local_image(quote, author)

    print("Uploading image to LinkedIn...")
    asset_urn = upload_image_to_linkedin(image_path)

    print("Publishing post...")
    post_url = post_to_linkedin(quote, author, asset_urn)
    print(f"Published! URL: {post_url}")

    print("Logging to history...")
    append_to_history(quote, author, post_url)

    print("Done!")

if __name__ == "__main__":
    main()
