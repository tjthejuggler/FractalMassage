import numpy as np
from PIL import Image, ImageDraw, ImageFont
import scipy.ndimage

def create_text_sdf(text, width=1024, height=512, font_size=150):
    # Create a black canvas
    img = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(img)
    
    # Try to load a clean Linux font, fallback to default if not found
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()
    
    # Center the text
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text(((width-w)/2, (height-h)/2), text, font=font, fill=255)
    
    # Convert to a NumPy array for SciPy math
    arr = np.array(img)
    inside = arr > 128
    outside = ~inside
    
    # Calculate distance to the edge of the letters
    dist_in = scipy.ndimage.distance_transform_edt(inside)
    dist_out = scipy.ndimage.distance_transform_edt(outside)
    
    # Combine: Negative is inside the letters, Positive is outside
    sdf = dist_in - dist_out
    
    # Map into a 0-255 grayscale texture where 128 is the exact edge
    sdf_scaled = np.clip(sdf * 4 + 128, 0, 255).astype(np.uint8)
    
    return sdf_scaled.tobytes(), width, height