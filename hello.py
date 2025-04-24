# First, make sure Pillow is installed:
# pip install Pillow

from PIL import Image, ImageDraw, ImageFont
import os

def main():
    # Path to the image file
    image_path = "self.jpg"
    
    try:
        # Check if the image exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Step 1: Open the image
        img = Image.open(image_path)
        print(f"✅ Successfully opened image: {image_path}")
        print(f"📏 Image size: {img.size}")
        print(f"🧾 Image format: {img.format}")
        print(f"🎨 Image mode: {img.mode}")
        
        # Step 2: Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
            print("🔄 Converted image to RGB mode")
        
        # Step 3: Access pixel data
        pixels = img.load()
        
        # Step 4: Modify pixels (draw a red square)
        square_size = 20
        for x in range(square_size):
            for y in range(square_size):
                pixels[x, y] = (255, 0, 0)  # Red

        print("🟥 Red square drawn in top-left corner.")

        # Step 5: Add text to image
        draw = ImageDraw.Draw(img)
        text = "Hello, Ashwani!"
        font = ImageFont.load_default()  # You can use truetype font as well

        text_position = (30, 30)
        text_color = (0, 255, 0)  # Green

        draw.text(text_position, text, fill=text_color, font=font)
        print("📝 Text added to the image.")
        
        # Step 6: Save the modified image
        modified_image_path = "modified_" + os.path.basename(image_path)
        img.save(modified_image_path)
        print(f"💾 Modified image saved as: {modified_image_path}")
        
        # Step 7: Check a modified pixel
        x, y = 10, 10
        print(f"🔍 Pixel at ({x}, {y}): {pixels[x, y]}")

        # Step 8: Show the image
        img.show()

    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    main()
