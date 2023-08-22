import os
import yaml
from cryptography.fernet import Fernet
from flask import current_app

KEYS_DIR = f"{current_app.app_context().config['WORKSPACE']}/.paperfly_keys"
KEYS_FILE = "keys.yaml"
KEY_FIELD = "encryption_key"
TOKEN_FIELD = "bearer_token"

def ensure_keys_dir_exists():
    if not os.path.exists(KEYS_DIR):
        os.mkdir(KEYS_DIR)

def generate_encryption_key():
    return Fernet.generate_key().decode()

def generate_bearer_token():
    return Fernet.generate_key().decode()

def save_keys_to_yaml(encryption_key, bearer_token):
    ensure_keys_dir_exists()
    with open(os.path.join(KEYS_DIR, KEYS_FILE), 'w') as file:
        yaml.dump({KEY_FIELD: encryption_key, TOKEN_FIELD: bearer_token}, file)

def load_encryption_key_from_yaml():
    with open(os.path.join(KEYS_DIR, KEYS_FILE), 'r') as file:
        config = yaml.safe_load(file)
        return config.get(KEY_FIELD)

def load_bearer_token_from_yaml():
    with open(os.path.join(KEYS_DIR, KEYS_FILE), 'r') as file:
        config = yaml.safe_load(file)
        return config.get(TOKEN_FIELD)

def config_exists():
    return os.path.exists(os.path.join(KEYS_DIR, KEYS_FILE))

def create_config_with_keys():
    if not config_exists():
        encryption_key = generate_encryption_key()
        bearer_token = generate_bearer_token()
        save_keys_to_yaml(encryption_key, bearer_token)