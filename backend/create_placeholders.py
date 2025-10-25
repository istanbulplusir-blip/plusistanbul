#!/usr/bin/env python3
"""
Create placeholder images for Peykan Tourism Platform
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Create defaults directory if it doesn't exist
os.makedirs('media/defaults', exist_ok=True)
os.makedirs('media/hero/desktop', exist_ok=True)
os.makedirs('media/hero/tablet', exist_ok=True)
os.makedirs('media/hero/mobile', exist_ok=True)

def create_placeholder(filename, text, size=(800, 600), bg_color='#f0f0f0', text_color='#666666'):
    """Create a placeholder image with text"""
    img = Image.new('RGB', size, bg_color)
    draw = ImageDraw.Draw(img)
    
    # Try to use a font, fallback to default if not available
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 40)
    except:
        try:
            font = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf', 40)
        except:
            font = ImageFont.load_default()
    
    # Calculate text position (center)
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    except:
        # Fallback for older PIL versions
        text_width, text_height = draw.textsize(text, font=font)
    
    position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
    
    # Draw text
    draw.text(position, text, fill=text_color, font=font)
    
    # Save image
    img.save(filename, 'PNG')
    print(f'Created: {filename}')

# Create placeholder images
print('Creating placeholder images...')

create_placeholder('media/defaults/no-image.png', 'No Image', (800, 600))
create_placeholder('media/defaults/tour-default.png', 'Tour Image', (800, 600))
create_placeholder('media/defaults/event-default.png', 'Event Image', (800, 600))
create_placeholder('media/defaults/venue-default.png', 'Venue Image', (800, 600))
create_placeholder('media/defaults/artist-default.png', 'Artist Image', (400, 400))
create_placeholder('media/defaults/transfer-default.png', 'Transfer Image', (800, 600))

# Create hero default images
create_placeholder('media/hero/desktop/PEYKAN-DEFAULT.png', 'Peykan Tourism', (1920, 1080), '#667eea', '#ffffff')
create_placeholder('media/hero/tablet/PEYKAN-DEFAULT.png', 'Peykan Tourism', (1024, 768), '#667eea', '#ffffff')
create_placeholder('media/hero/mobile/PEYKAN-DEFAULT.png', 'Peykan Tourism', (768, 1024), '#667eea', '#ffffff')

print('\nAll placeholder images created successfully!')
print('Total images created: 9')
