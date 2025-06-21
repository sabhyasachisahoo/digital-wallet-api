from functools import wraps
from flask import request, jsonify
import base64
import bcrypt
from .models import User

def authenticate(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization')
        if not auth or not auth.startswith('Basic '):
            return jsonify({'error': 'Unauthorized'}), 401
        encoded_credentials = auth.split(' ')[1]
        username, password = base64.b64decode(encoded_credentials).decode().split(':')
        user = User.query.filter_by(username=username).first()
        if not user or not bcrypt.checkpw(password.encode(), user.password.encode()):
            return jsonify({'error': 'Unauthorized'}), 401
        request.user = user
        return f(*args, **kwargs)
    return decorated
