# Create a placeholder image for products without images
from PIL import Image, ImageDraw, ImageFont
import os

def create_placeholder_image():
    # Create a 300x300 image with a light gray background
    img = Image.new('RGB', (300, 300), color='#f3f4f6')
    draw = ImageDraw.Draw(img)
    
    # Draw a simple icon/text
    try:
        # Try to use a default font
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    # Draw a box icon
    draw.rectangle([75, 75, 225, 225], outline='#9ca3af', width=3)
    
    # Add text
    text = "No Image"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (300 - text_width) // 2
    y = 240
    draw.text((x, y), text, fill='#6b7280', font=font)
    
    # Save the image
    static_images_dir = 'static/images'
    os.makedirs(static_images_dir, exist_ok=True)
    img.save(os.path.join(static_images_dir, 'product-placeholder.png'))
    print("✅ Created placeholder image: static/images/product-placeholder.png")

if __name__ == "__main__":
    create_placeholder_image()