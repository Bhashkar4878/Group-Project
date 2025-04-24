from PIL import Image
import stepic

def hide_message_in_image():
    # Load your original image
    img = Image.open("self.jpg")  # Make sure 'self.jpg' is in the same folder
    
    # Your secret message
    secret_message = "This is a secret message from Ashwlr3knhvij!"  # Customize your message
    
    # Encode the message into the image
    encoded_img = stepic.encode(img, secret_message.encode())
    
    # Save the new image with the hidden secret message
    encoded_img.save("encoded_self.png")  # Save as PNG to preserve data

    print("🔐 Secret message has been hidden in 'encoded_self.png'")

# Call the function
hide_message_in_image()
