from cryptography.fernet import Fernet
from .key_generator import load_encryption_key_from_yaml

def encrypt_content(content):
    key = load_encryption_key_from_yaml()
    cipher_suite = Fernet(key.encode())
    encrypted_content = cipher_suite.encrypt(content.encode())
    return encrypted_content

def decrypt_content(encrypted_content):
    key = load_encryption_key_from_yaml()
    cipher_suite = Fernet(key.encode())
    decrypted_content = cipher_suite.decrypt(encrypted_content).decode()
    return decrypted_content
