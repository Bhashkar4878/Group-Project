from PIL import Image
import stepic

def extract_message_from_image():
    # Load the image that has the secret message
    encoded_img = Image.open("encoded_self.png")  # Path to the image with the hidden message
    
    # Decode the message
    decoded_message = stepic.decode(encoded_img)

    print("📩 Secret message retrieved:")
    print(decoded_message)

# Call the function
extract_message_from_image()
