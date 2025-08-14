from flask import Blueprint, request, jsonify
from passlib.hash import bcrypt
import jwt
import datetime
from functools import wraps
from .database import db
from .config import config
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

def auth_required(f):
    """Decorator to require JWT authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            # Decode token
            payload = jwt.decode(token, config.JWT_SECRET, algorithms=['HS256'])
            current_user = db.users.find_one({'username': payload['username']})
            
            if not current_user:
                return jsonify({'message': 'Invalid token'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

@auth_bp.route('/api/register', methods=['POST'])
def register():
    """Register a new user."""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'message': 'Username and password are required'}), 400
        
        username = data['username'].strip()
        password = data['password']
        
        # Check if username already exists
        if db.users.find_one({'username': username}):
            return jsonify({'message': 'Username already exists'}), 409
        
        # Hash password
        hashed_password = bcrypt.hash(password)
        
        # Create user
        user = {
            'username': username,
            'password': hashed_password,
            'created_at': datetime.datetime.utcnow()
        }
        
        db.users.insert_one(user)
        
        # Generate JWT token
        token = jwt.encode(
            {
                'username': username,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            },
            config.JWT_SECRET,
            algorithm='HS256'
        )
        
        return jsonify({
            'message': 'User registered successfully',
            'token': token,
            'username': username
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@auth_bp.route('/api/login', methods=['POST'])
def login():
    """Login user and return JWT token."""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'message': 'Username and password are required'}), 400
        
        username = data['username'].strip()
        password = data['password']
        
        # Find user
        user = db.users.find_one({'username': username})
        
        if not user or not bcrypt.verify(password, user['password']):
            return jsonify({'message': 'Invalid username or password'}), 401
        
        # Generate JWT token
        token = jwt.encode(
            {
                'username': username,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            },
            config.JWT_SECRET,
            algorithm='HS256'
        )
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'username': username
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@auth_bp.route('/api/history', methods=['GET'])
@auth_required
def get_history(current_user):
    """Get user's chat history."""
    try:
        username = current_user['username']
        
        # Get last 50 messages for the user
        messages = list(db.messages.find(
            {'username': username},
            {'_id': 0}  # Exclude MongoDB _id
        ).sort('created_at', -1).limit(50))
        
        # Reverse to show oldest first
        messages.reverse()
        
        return jsonify({
            'messages': messages
        }), 200
        
    except Exception as e:
        logger.error(f"History error: {e}")
        return jsonify({'message': 'Internal server error'}), 500



