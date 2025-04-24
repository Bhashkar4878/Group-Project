# First, make sure Pillow is installed:
# pip install Pillow

from PIL import Image
import os
from PIL import ImageDraw, ImageFont


def main():
    # Path to the image file
    image_path = "self.jpg"
    
    try:
        # Check if the image file exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Step 1: Open the image
        img = Image.open(image_path)
        print(f"✅ Successfully opened image: {image_path}")
        print(f"📏 Image size: {img.size}")
        print(f"🧾 Image format: {img.format}")
        print(f"🎨 Image mode: {img.mode}")  # Example: RGB, RGBA, etc.
        
        # Step 2: Convert to RGB if not already
        if img.mode != 'RGB':
            img = img.convert('RGB')
            print("🔄 Converted image to RGB mode")
        
        # Step 3: Access pixel data
        pixels = img.load()
        
        # Step 4: Modify a square of pixels in the top-left corner
        square_size = 20
        for x in range(square_size):
            for y in range(square_size):
                pixels[x, y] = (255, 0, 0)  # Red
        
        # Step 5: Save the modified image
        modified_image_path = "modified_" + os.path.basename(image_path)
        img.save(modified_image_path)
        print(f"💾 Modified image saved as: {modified_image_path}")
        
        # Step 6: Display pixel data at a known location (inside the modified area)
        x, y = 10, 10
        print(f"🔍 Pixel at ({x}, {y}): {pixels[x, y]}")

        # Optional: Show the image (opens in default viewer)
        img.show()

    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    main()
