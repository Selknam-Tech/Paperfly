from functools import wraps
from flask import request, jsonify
import os

BEARER_TOKEN = os.environ.get('BEARER_TOKEN', 'tu_token_estatico_secreto')

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