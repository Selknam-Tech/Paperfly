import os
import yaml
from cryptography.fernet import Fernet
from flask import current_app

CONFIG_DIR = f"{current_app.config['WORKSPACE']}/.paperfly"
CONFIG_FILE = "config.yaml"
KEY_FIELD = "encryption_key"

def ensure_config_dir_exists():
    if not os.path.exists(CONFIG_DIR):
        os.mkdir(CONFIG_DIR)

def generate_encryption_key():
    return Fernet.generate_key().decode()

def save_encryption_key_to_yaml(key):
    ensure_config_dir_exists()
    with open(os.path.join(CONFIG_DIR, CONFIG_FILE), 'w') as file:
        yaml.dump({KEY_FIELD: key}, file)

def load_encryption_key_from_yaml():
    with open(os.path.join(CONFIG_DIR, CONFIG_FILE), 'r') as file:
        config = yaml.safe_load(file)
        return config.get(KEY_FIELD)

def config_exists():
    return os.path.exists(os.path.join(CONFIG_DIR, CONFIG_FILE))

def create_config_with_encryption_key():
    if not config_exists():
        key = generate_encryption_key()
        save_encryption_key_to_yaml(key)

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
