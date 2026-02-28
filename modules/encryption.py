from cryptography.fernet import Fernet
import base64
import os

# Generate key once and keep constant
KEY = base64.urlsafe_b64encode(b"12345678901234567890123456789012")
cipher = Fernet(KEY)

def encrypt_data(data):
    return cipher.encrypt(data.encode()).decode()

def decrypt_data(data):
    return cipher.decrypt(data.encode()).decode()