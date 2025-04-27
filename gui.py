import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from PIL import Image, ImageTk
import numpy as np
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64
import binascii
import os

# AES encryption
def encrypt_message(message, key):
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(message.encode('utf-8'), AES.block_size))
    return base64.b64encode(cipher.iv + ct_bytes).decode('utf-8')

def decrypt_message(cipher_text, key):
    try:
        raw = base64.b64decode(cipher_text)
        iv = raw[:16]
        ct = raw[16:]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(ct), AES.block_size)
        return decrypted.decode('utf-8', errors='replace')  # Use 'replace' to handle invalid bytes
    except Exception as e:
        raise ValueError(f"Decryption failed. Check if you're using the correct AES key: {e}")

# UTF-8 safe steganography
def to_bin(data):
    return ''.join(format(byte, '08b') for byte in data.encode('utf-8'))

def from_bin(bin_str):
    try:
        byte_chunks = [bin_str[i:i+8] for i in range(0, len(bin_str), 8)]
        byte_data = bytes([int(b, 2) for b in byte_chunks])
        return byte_data.decode('utf-8', errors='replace')  # Use 'replace' to handle invalid bytes
    except Exception as e:
        raise ValueError(f"Error decoding binary data: {e}")

def encode_image(image_path, message, output_path):
    img = Image.open(image_path).convert('RGB')
    data = np.asarray(img, dtype=np.uint8)
    flat_data = data.reshape(-1).copy()
    
    bin_msg = to_bin(message) + '1111111111111110'  # End delimiter
    if len(bin_msg) > len(flat_data):
        raise ValueError("Message too long to encode in this image.")
    
    for i in range(len(bin_msg)):
        # Safer bit manipulation ensuring values stay within 0-255
        if int(bin_msg[i]) == 1:
            flat_data[i] = flat_data[i] | 1  # Set LSB to 1
        else:
            flat_data[i] = flat_data[i] & 254  # Set LSB to 0 (254 is 11111110 in binary)
    
    encoded_data = flat_data.reshape(data.shape)
    encoded_img = Image.fromarray(encoded_data.astype(np.uint8))
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
        raise ValueError("No hidden message found. This image may not contain a hidden message.")

# GUI App
class PixelVaultApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pixel Vault - Secure Image Steganography")
        self.root.geometry("700x650")
        self.root.configure(bg="#f0f0f0")
        
        # Set app icon if available
        try:
            self.root.iconbitmap("pixel_vault_icon.ico")
        except:
            pass
        
        # Main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title and description
        title_label = ttk.Label(main_frame, text="Pixel Vault", font=("Helvetica", 24, "bold"))
        title_label.pack(pady=(0, 5))
        
        desc_label = ttk.Label(main_frame, text="Hide encrypted messages in images securely", font=("Helvetica", 12))
        desc_label.pack(pady=(0, 20))
        
        # Notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Encode tab
        # Scrollable Encode Frame Setup
        encode_container = ttk.Frame(notebook)
        notebook.add(encode_container, text="Encode")

        encode_canvas = tk.Canvas(encode_container)
        scrollbar = ttk.Scrollbar(encode_container, orient="vertical", command=encode_canvas.yview)

        scrollable_encode_frame = ttk.Frame(encode_canvas)

        scrollable_encode_frame.bind(
            "<Configure>",
            lambda e: encode_canvas.configure(
            scrollregion=encode_canvas.bbox("all")
            )
        )

        encode_canvas.create_window((0, 0), window=scrollable_encode_frame, anchor="nw")
        encode_canvas.configure(yscrollcommand=scrollbar.set)

        encode_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        
        # Decode tab
        decode_frame = ttk.Frame(notebook, padding="10")
        notebook.add(decode_frame, text="Decode")
        
        # Encode tab content
        ttk.Label(scrollable_encode_frame, text="Enter your secret message:", font=("Helvetica", 11)).pack(anchor='w', pady=(5, 2))
        
        self.message_entry = tk.Text(scrollable_encode_frame, height=8, width=60)
        self.message_entry.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        encode_button_frame = ttk.Frame(scrollable_encode_frame)
        encode_button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(encode_button_frame, text="Select Image", command=self.select_encode_image).pack(side=tk.LEFT, padx=5)
        self.encode_button = ttk.Button(encode_button_frame, text="Encode Message", command=self.encode, state=tk.DISABLED)
        self.encode_button.pack(side=tk.LEFT, padx=5)
        
        self.encode_image_label = ttk.Label(scrollable_encode_frame, text="No image selected")
        self.encode_image_label.pack(pady=5)
        
        self.image_preview_encode = ttk.Label(scrollable_encode_frame)
        self.image_preview_encode.pack(pady=10)
        
        self.encode_output_frame = ttk.LabelFrame(scrollable_encode_frame, text="Encryption Results", padding="10")
        self.encode_output_frame.pack(fill=tk.X, pady=10)
        
        self.output_label = ttk.Label(self.encode_output_frame, text="", wraplength=600)
        self.output_label.pack(fill=tk.X)
        
        # Key result frame
        self.key_frame = ttk.Frame(self.encode_output_frame)
        self.key_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.key_label = ttk.Label(self.key_frame, text="")
        self.key_label.pack(side=tk.LEFT)
        
        self.copy_key_button = ttk.Button(self.key_frame, text="Copy Key", command=self.copy_key, state=tk.DISABLED)
        self.copy_key_button.pack(side=tk.LEFT, padx=5)
        
        # Decode tab content
        ttk.Button(decode_frame, text="Select Encoded Image", command=self.select_decode_image).pack(pady=10)
        
        self.decode_image_label = ttk.Label(decode_frame, text="No image selected")
        self.decode_image_label.pack(pady=5)
        
        self.image_preview_decode = ttk.Label(decode_frame)
        self.image_preview_decode.pack(pady=10)
        
        key_frame = ttk.Frame(decode_frame)
        key_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(key_frame, text="AES Key:").pack(side=tk.LEFT)
        
        self.key_entry = ttk.Entry(key_frame, width=40)
        self.key_entry.pack(side=tk.LEFT, padx=5)
        
        self.decode_button = ttk.Button(decode_frame, text="Decode Message", command=self.decode, state=tk.DISABLED)
        self.decode_button.pack(pady=10)
        
        decode_output_frame = ttk.LabelFrame(decode_frame, text="Decoded Message", padding="10")
        decode_output_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.decoded_message = tk.Text(decode_output_frame, height=8, width=60, wrap=tk.WORD)
        self.decoded_message.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w")
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Key generation
        self.key = get_random_bytes(16)
        self.selected_encode_image = None
        self.selected_decode_image = None
    
    def select_encode_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Image to Encode",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")]
        )
        if file_path:
            self.selected_encode_image = file_path
            self.encode_image_label.config(text=os.path.basename(file_path))
            self.encode_button.config(state=tk.NORMAL)
            self.status_var.set(f"Selected image: {os.path.basename(file_path)}")
            self.display_image_preview(file_path, self.image_preview_encode)
    
    def select_decode_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Encoded Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")]
        )
        if file_path:
            self.selected_decode_image = file_path
            self.decode_image_label.config(text=os.path.basename(file_path))
            self.decode_button.config(state=tk.NORMAL)
            self.status_var.set(f"Selected encoded image: {os.path.basename(file_path)}")
            self.display_image_preview(file_path, self.image_preview_decode)
    
    def display_image_preview(self, file_path, label):
        try:
            img = Image.open(file_path)
            # Resize for preview
            img.thumbnail((200, 200))
            photo = ImageTk.PhotoImage(img)
            label.config(image=photo)
            label.image = photo  # Keep a reference
        except Exception as e:
            messagebox.showerror("Preview Error", f"Failed to load image preview: {e}")
    
    def encode(self):
        if not self.selected_encode_image:
            messagebox.showerror("Error", "Please select an image first")
            return
        
        message = self.message_entry.get("1.0", tk.END).strip()
        if not message:
            messagebox.showerror("Error", "Please enter a message to hide")
            return
        
        encrypted = encrypt_message(message, self.key)
        
        output_path = filedialog.asksaveasfilename(
            defaultextension=".png", 
            title="Save Encoded Image",
            filetypes=[("PNG files", "*.png")]
        )
        if not output_path:
            return
        
        try:
            self.status_var.set("Encoding message...")
            self.root.update()
            
            encode_image(self.selected_encode_image, encrypted, output_path)
            
            self.output_label.config(text=f"✅ Message successfully hidden in: {os.path.basename(output_path)}")
            self.key_label.config(text=f"🔐 AES Key: {self.key.hex()}")
            self.copy_key_button.config(state=tk.NORMAL)
            self.status_var.set("Message encoded successfully")
            
            messagebox.showinfo("Success", 
                               f"Message hidden successfully!\n\n"
                               f"IMPORTANT: Save this key to decode later:\n{self.key.hex()}\n\n"
                               f"Without this key, you won't be able to recover your message.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status_var.set("Encoding failed")
    
    def copy_key(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.key.hex())
        self.status_var.set("AES key copied to clipboard")
    
    def decode(self):
        if not self.selected_decode_image:
            messagebox.showerror("Error", "Please select an encoded image first")
            return
        
        key_hex = self.key_entry.get().strip()
        if not key_hex or len(key_hex) != 32:
            messagebox.showerror("Error", "Invalid AES key length. Required: 32 hex characters.")
            return
        
        try:
            self.status_var.set("Decoding message...")
            self.root.update()
            
            encrypted = decode_image(self.selected_decode_image)
            
            try:
                decrypted = decrypt_message(encrypted, binascii.unhexlify(key_hex))
                self.decoded_message.delete("1.0", tk.END)
                self.decoded_message.insert("1.0", decrypted)
                self.status_var.set("Message decoded successfully")
            except ValueError as e:
                messagebox.showerror("Decryption Error", 
                                    f"Could not decrypt the message. Make sure you're using the correct AES key.\n\nTechnical details: {e}")
                self.status_var.set("Decryption failed - wrong key?")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to decode image: {e}")
            self.status_var.set("Decoding failed")

# Run the GUI app
if __name__ == "__main__":
    root = tk.Tk()
    app = PixelVaultApp(root)
    root.mainloop()
