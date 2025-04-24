import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image
import numpy as np
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64
import binascii

# AES encryption
def encrypt_message(message, key):
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(message.encode('utf-8'), AES.block_size))
    return base64.b64encode(cipher.iv + ct_bytes).decode('utf-8')

def decrypt_message(cipher_text, key):
    raw = base64.b64decode(cipher_text)
    iv = raw[:16]
    ct = raw[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ct), AES.block_size).decode('utf-8')

# UTF-8 safe steganography
def to_bin(data):
    return ''.join(format(byte, '08b') for byte in data.encode('utf-8'))

def from_bin(bin_str):
    byte_chunks = [bin_str[i:i+8] for i in range(0, len(bin_str), 8)]
    byte_data = bytes([int(b, 2) for b in byte_chunks])
    return byte_data.decode('utf-8')

def encode_image(image_path, message, output_path):
    img = Image.open(image_path).convert('RGB')
    data = np.asarray(img, dtype=np.uint8)  # ✅ Force uint8 array
    flat_data = data.reshape(-1).copy()     # ✅ Flatten and copy

    bin_msg = to_bin(message) + '1111111111111110'  # End delimiter
    if len(bin_msg) > len(flat_data):
        raise ValueError("Message too long to encode in this image.")

    for i in range(len(bin_msg)):
        flat_data[i] = (flat_data[i] & ~1) | int(bin_msg[i])

    encoded_data = flat_data.reshape(data.shape)
    encoded_img = Image.fromarray(encoded_data.astype(np.uint8))  # ✅ Keep uint8
    encoded_img.save(output_path)

def decode_image(image_path):
    img = Image.open(image_path)
    data = np.array(img, dtype=np.uint8).reshape(-1)
    bits = [str(pixel & 1) for pixel in data]
    bin_str = ''.join(bits)
    end_index = bin_str.find('1111111111111110')
    if end_index != -1:
        bin_msg = bin_str[:end_index]
        return from_bin(bin_msg)
    else:
        raise ValueError("No hidden message found.")

# GUI App
class StegoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AES Steganography Tool")

        self.message_entry = tk.Text(root, height=5, width=50)
        self.message_entry.pack(pady=10)

        self.encode_button = tk.Button(root, text="Encode Message", command=self.encode)
        self.encode_button.pack(pady=5)

        self.decode_button = tk.Button(root, text="Decode Message", command=self.decode)
        self.decode_button.pack(pady=5)

        self.output_label = tk.Label(root, text="", fg="green")
        self.output_label.pack(pady=10)

        self.key = get_random_bytes(16)  # ✅ Auto AES key per session

    def encode(self):
        file_path = filedialog.askopenfilename(title="Select Image to Encode")
        if not file_path:
            return
        message = self.message_entry.get("1.0", tk.END).strip()
        encrypted = encrypt_message(message, self.key)

        output_path = filedialog.asksaveasfilename(defaultextension=".png", title="Save Stego Image")
        if not output_path:
            return

        try:
            encode_image(file_path, encrypted, output_path)
            self.output_label.config(text=f"✅ Message hidden.\n🔐 AES Key: {self.key.hex()}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def decode(self):
        file_path = filedialog.askopenfilename(title="Select Stego Image")
        if not file_path:
            return

        key_hex = simpledialog.askstring("AES Key", "Enter 32-character hex AES Key:")
        if not key_hex or len(key_hex) != 32:
            messagebox.showerror("Error", "Invalid AES key length. Required: 32 hex characters.")
            return

        try:
            encrypted = decode_image(file_path)
            decrypted = decrypt_message(encrypted, binascii.unhexlify(key_hex))
            self.output_label.config(text=f"📩 Decoded Message:\n{decrypted}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

# Run the GUI app
if __name__ == "__main__":
    root = tk.Tk()
    app = StegoApp(root)
    root.mainloop()
