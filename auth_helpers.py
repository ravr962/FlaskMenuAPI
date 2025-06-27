import jwt
from functools import wraps
from flask import request, jsonify
from models.user import User
import os

SECRET_KEY = os.getenv("SECRET_KEY")

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            bearer = request.headers['Authorization']
            token = bearer.split(" ")[1] if " " in bearer else bearer

        if not token:
            #return jsonify({'error': 'Token is missing'}), 401
            return {'error': 'Token is missing'}, 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                #return jsonify({'error': 'User not found'}), 401
                return {"error": "User not found"}, 401
        except jwt.ExpiredSignatureError:
            #return jsonify({'error': 'Token expired'}), 401
            return {'error': 'Token expired'}, 401
        except jwt.InvalidTokenError:
            #return jsonify({'error': 'Invalid token'}), 401
            return {'error': 'Invalid token'}, 401

        return f(current_user, *args, **kwargs)

    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            bearer = request.headers['Authorization']
            token = bearer.split(" ")[1] if " " in bearer else bearer

        if not token:
            #return jsonify({'error': 'Token is missing'}), 401
            return {'error': 'Token is missing'}, 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = User.query.get(data["user_id"])
            if not current_user:
                #return jsonify({"error": "User not found"}), 401
                return {"error": "User not found"}, 401
            if not current_user.is_admin:
                #return jsonify({"error": "Admin access required"}), 403
                return {"error": "Admin access required"}, 403
        except jwt.ExpiredSignatureError:
            #return jsonify({'error': 'Token expired'}), 401
            return {'error': 'Token expired'}, 401
        except jwt.InvalidTokenError:
            #return jsonify({'error': 'Invalid token'}), 401
            return {'error': 'Invalid token'}, 401

        return f(*args, **kwargs)
    return decorated

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = None
            if 'Authorization' in request.headers:
                bearer = request.headers['Authorization']
                token = bearer.split(" ")[1] if " " in bearer else bearer

            if not token:
                #return jsonify({'error': 'Token is missing'}), 401
                return {'error': 'Token is missing'}, 401

            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                user = User.query.get(payload['user_id'])

                if not user:
                    #return jsonify({'error': 'User not found'}), 401
                    return {"error": "User not found"}, 401
                if user.role not in roles:
                    #return jsonify({'error': 'Access forbidden for this role'}), 403
                    return {'error': 'Access forbidden for this role'}, 403

            except jwt.ExpiredSignatureError:
                #return jsonify({'error': 'Token expired'}), 401
                return {'error': 'Token expired'}, 401
            except jwt.InvalidTokenError:
                #return jsonify({'error': 'Invalid token'}), 401
                return {'error': 'Invalid token'}, 401

            return f(*args, **kwargs)
        return decorated_function
    return decorator