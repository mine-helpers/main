from functools import wraps
from flask import g, request, jsonify
from .errors import forbidden
from ..models import User


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.current_user.can(permission):
                return forbidden('Insufficient permissions')
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def check_token():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            access_token = request.headers.get('Authorization')
            if access_token is None:
                res = jsonify({'error': 'No Bearer token added to Authorization header'})
                res.status_code = 401
                return res
            token = access_token.split('Bearer ')[1]
            user = User.verify_auth_token(token)
            if user is None:
                res = jsonify({'error': '401 Unauthorized to access resource'})
                res.status_code = 401
                return res
            g.current_user = user
            g.token_used   = True
            return f(*args, **kwargs)
        return decorated_function
    return decorator
