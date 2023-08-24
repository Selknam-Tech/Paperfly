import yaml
from functools import wraps
from flask import request, jsonify, current_app
import os


# Configuración del archivo y ruta
CONFIG_DIR = f"{current_app.config['WORKSPACE']}/.paperfly_key/"
CONFIG_FILE = "keys.yaml"
TOKEN_FIELD = "bearer_token"

# Función para cargar el bearer token desde el archivo YAML
def load_bearer_token_from_yaml():
    with open(os.path.join(CONFIG_DIR, CONFIG_FILE), 'r') as file:
        config = yaml.safe_load(file)
        return config.get(TOKEN_FIELD)

# Intenta obtener el bearer token desde el archivo YAML o utiliza el valor por defecto.
BEARER_TOKEN = load_bearer_token_from_yaml() or os.environ.get('BEARER_TOKEN', 'miss_token')

def require_token(f):
    @wraps(f)
    def decorated_function(*args, **kws):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify(error="missing token"), 403
        if token.split(" ")[1] != BEARER_TOKEN:
            return jsonify(error="invalid token"), 403
        return f(*args, **kws)
    return decorated_function