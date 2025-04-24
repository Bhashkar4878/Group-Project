from PIL import Image
import numpy as np
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64

def encrypt_message(message, key):
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(message.encode(), AES.block_size))
    return base64.b64encode(cipher.iv + ct_bytes).decode()

def decrypt_message(cipher_text, key):
    raw = base64.b64decode(cipher_text)
    iv = raw[:16]
    ct = raw[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ct), AES.block_size).decode()

def to_bin(data):
    return ''.join(format(ord(c), '08b') for c in data)

def from_bin(bin_str):
    chars = [bin_str[i:i+8] for i in range(0, len(bin_str), 8)]
    return ''.join([chr(int(c, 2)) for c in chars])

def encode_image(image_path, message, output_path):
    img = Image.open(image_path).convert('RGB')
    data = np.array(img)

    flat_data = data.flatten()
    bin_msg = to_bin(message) + '1111111111111110'  # End delimiter
    if len(bin_msg) > len(flat_data):
        raise ValueError("Message too long to encode.")

    for i in range(len(bin_msg)):
        # Ensure the modification respects the pixel value range (0-255)
        flat_data[i] = (flat_data[i] & ~1) | int(bin_msg[i])

    # Reshape the modified data back to the original image shape
    encoded_data = flat_data.reshape(data.shape)
    encoded_img = Image.fromarray(encoded_data.astype('uint8'))
    encoded_img.save(output_path)

def decode_image(image_path):
    img = Image.open(image_path)
    data = np.array(img).flatten()
    bits = [str(pixel & 1) for pixel in data]

    bin_str = ''.join(bits)
    end_index = bin_str.find('1111111111111110')
    if end_index != -1:
        bin_msg = bin_str[:end_index]
        return from_bin(bin_msg)
    else:
        raise ValueError("No hidden message found.")

if __name__ == "__main__":
    secret_message = "This is a secret communication."
    key = get_random_bytes(16)  # Securely store/share this key

    encrypted = encrypt_message(secret_message, key)
    encode_image("self.jpg", encrypted, "output.png")

    print("Message hidden successfully in output.png")

    # Receiver Side
    hidden_encrypted = decode_image("output.png")
    decrypted = decrypt_message(hidden_encrypted, key)

    print("Decrypted Message:", decrypted)
