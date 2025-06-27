from flask import Blueprint, request, jsonify
from models.user import User
from models import db
import jwt
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import os

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
SECRET_KEY = os.getenv("SECRET_KEY")

@auth_bp.route('/register', methods=['POST'])
@auth_bp.route('/register/', methods=['POST'])
def register():
    data = request.get_json()
    if not data.get('username') or not data.get('password'):
        return {'error': 'Username and password required'}, 400
    
    if User.query.filter_by(username=data['username']).first():
        return {'error': 'Username already exists'}, 409

    user = User(username=data['username'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return {'message': 'User created'}, 201

@auth_bp.route('/login', methods=['POST'])
@auth_bp.route('/login/', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()

    if user and user.check_password(data['password']):
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=2)
        }, SECRET_KEY, algorithm='HS256')
        return {'token': token}
    
    return {'error': 'Invalid credentials'}, 401
