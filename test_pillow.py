from PIL import Image, ImageDraw, ImageFont
import textwrap

def draw_text():
    img = Image.open('template.png')
    draw = ImageDraw.Draw(img)
    
    # We will try a few bounding boxes
    text = "Success is not final, failure is not fatal: it is the courage to continue that counts."
    
    font = ImageFont.truetype('C:\\\\Windows\\\\Fonts\\\\arialbd.ttf', 40)
    
    width, height = img.size
    
    # Text wrapping
    margin = 250
    offset = 40
    
    lines = textwrap.wrap(text, width=25)
    
    # Calculate total text height
    total_text_height = sum([draw.textbbox((0, 0), line, font=font)[3] for line in lines])
    
    # Start y
    y_text = (height - total_text_height) / 2
    
    for line in lines:
        line_width = draw.textbbox((0, 0), line, font=font)[2]
        x_text = (width - line_width) / 2
        draw.text((x_text, y_text), line, font=font, fill=(255, 255, 255))
        y_text += draw.textbbox((0, 0), line, font=font)[3] + 10
        
    img.save('output_test.png')

draw_text()
