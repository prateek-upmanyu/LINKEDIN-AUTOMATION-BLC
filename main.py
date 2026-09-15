import os
import time
from datetime import datetime
import requests
import google.generativeai as genai

# Environment Variables
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
LINKEDIN_ACCESS_TOKEN = os.environ.get("LINKEDIN_ACCESS_TOKEN")
LINKEDIN_AUTHOR_URN = os.environ.get("LINKEDIN_AUTHOR_URN") # e.g., urn:li:person:123456789

def get_previous_quotes():
    import os
    if not os.path.exists('history.txt'):
        return []
    with open('history.txt', 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def generate_unique_quote(previous_quotes):
    genai.configure(api_key=GEMINI_API_KEY)
    # Using Gemini 1.5 Flash for quick text generation
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = "Generate a short, catchy, and highly motivating 1-2 sentence quote related to sales, cold calling, lead generation, or telecalling. It should align with the mindset of using a 'Bulk Leads Caller' app to maximize sales. Just provide the quote text, nothing else. No quote marks."
    
    for _ in range(5): # Try 5 times to get a unique quote
        response = model.generate_content(prompt)
        quote = response.text.strip().strip('"').strip("'")
        
        # Check similarity (basic exact match/substring match here, can be improved)
        is_duplicate = False
        for prev in previous_quotes:
            if quote.lower() in prev.lower() or prev.lower() in quote.lower():
                is_duplicate = True
                break
                
        if not is_duplicate:
            return quote
            
    raise Exception("Failed to generate a unique quote after 5 attempts.")

def create_local_image(quote):
    from PIL import Image, ImageDraw, ImageFont
    import textwrap
    import os

    template_path = 'template.png'
    output_path = 'quote.png'
    
    if not os.path.exists(template_path):
        raise Exception(f"Template image {template_path} not found.")

    img = Image.open(template_path)
    draw = ImageDraw.Draw(img)
    
    font_path = 'montserrat.ttf'
    if not os.path.exists(font_path):
        import urllib.request
        # Download a free font (Roboto) directly
        font_url = "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Bold.ttf"
        try:
            urllib.request.urlretrieve(font_url, font_path)
        except Exception as e:
            print(f"Failed to download font, using default: {e}")
            
    try:
        font = ImageFont.truetype(font_path, 40)
    except Exception:
        # Fallback for local windows test
        try:
            font = ImageFont.truetype('C:\\Windows\\Fonts\\arialbd.ttf', 40)
        except Exception:
            font = ImageFont.load_default()
        
    width, height = img.size
    
    # Wrap text to fit perfectly between the two telephone icons
    # Reduced width to ensure it doesn't overlap with the icons on the sides
    lines = textwrap.wrap(quote, width=22)
    
    # Calculate total text height
    total_text_height = sum([draw.textbbox((0, 0), line, font=font)[3] for line in lines])
    
    # Start y to center vertically
    y_text = (height - total_text_height) / 2
    
    for line in lines:
        line_width = draw.textbbox((0, 0), line, font=font)[2]
        x_text = (width - line_width) / 2
        draw.text((x_text, y_text), line, font=font, fill=(255, 255, 255))
        y_text += draw.textbbox((0, 0), line, font=font)[3] + 15
        
    img.save(output_path)
    return output_path

def upload_image_to_linkedin(image_path):
    # 1. Register Upload
    register_url = "https://api.linkedin.com/v2/assets?action=registerUpload"
    headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    
    register_body = {
        "registerUploadRequest": {
            "recipes": [
                "urn:li:digitalmediaRecipe:feedshare-image"
            ],
            "owner": LINKEDIN_AUTHOR_URN,
            "serviceRelationships": [
                {
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent"
                }
            ]
        }
    }
    
    res = requests.post(register_url, headers=headers, json=register_body)
    res_data = res.json()
    
    upload_url = res_data['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
    asset_urn = res_data['value']['asset']
    
    # 2. Upload Image
    with open(image_path, 'rb') as f:
        image_data = f.read()
        
    upload_headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
    }
    upload_res = requests.put(upload_url, headers=upload_headers, data=image_data)
    if upload_res.status_code != 201:
        raise Exception("Failed to upload image to LinkedIn.")
        
    return asset_urn

def post_to_linkedin(quote, asset_urn):
    post_url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    
    post_body = {
        "author": LINKEDIN_AUTHOR_URN,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": f"{quote}\n\n#Motivation #DailyQuote #Inspiration"
                },
                "shareMediaCategory": "IMAGE",
                "media": [
                    {
                        "status": "READY",
                        "description": {"text": "Daily Quote"},
                        "media": asset_urn,
                        "title": {"text": "Daily Quote"}
                    }
                ]
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    
    res = requests.post(post_url, headers=headers, json=post_body)
    if res.status_code != 201:
        raise Exception(f"Failed to post to LinkedIn: {res.text}")
        
    # Construct URL (approximation, true URL requires additional API calls, but returning the URN is typical)
    post_id = res.json().get('id')
    return f"https://www.linkedin.com/feed/update/{post_id}"

def append_to_history(quote, post_url):
    from datetime import datetime
    date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open('history.txt', 'a', encoding='utf-8') as f:
        f.write(f"{date_str} | {quote} | {post_url}\n")

def main():
    print("Starting Daily LinkedIn Quote Publisher...")
    
    print("Fetching previous quotes...")
    previous_quotes = get_previous_quotes()
    
    print("Generating new unique quote...")
    quote = generate_unique_quote(previous_quotes)
    print(f"Generated Quote: {quote}")
    
    print("Creating quote image locally...")
    image_path = create_local_image(quote)
    
    print("Uploading image to LinkedIn...")
    asset_urn = upload_image_to_linkedin(image_path)
    
    print("Publishing post...")
    post_url = post_to_linkedin(quote, asset_urn)
    print(f"Published successfully! URL: {post_url}")
    
    print("Logging to local history...")
    append_to_history(quote, post_url)
    
    print("Workflow completed successfully!")

if __name__ == "__main__":
    main()
