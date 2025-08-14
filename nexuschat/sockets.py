from flask_socketio import emit, disconnect
from flask import request, session as socket_session
import jwt
import datetime
from .database import db
from .config import config
from .ai import generate_ai_reply
import logging

logger = logging.getLogger(__name__)

# Track connected users by Socket.IO session id
_connected_sid_to_username = {}

def _get_username_from_context():
	"""Resolve username from session/map, or from token in query string as a fallback."""
	username = socket_session.get('username') or _connected_sid_to_username.get(request.sid)
	if username:
		return username
	# Fallback: try decoding token again from the request args
	token = request.args.get('token')
	if not token:
		return None
	try:
		payload = jwt.decode(token, config.JWT_SECRET, algorithms=['HS256'])
		username = payload.get('username')
		if username:
			# Cache for subsequent events
			_connected_sid_to_username[request.sid] = username
			socket_session['username'] = username
		return username
	except Exception:
		return None

def _bind_username_from_token(token: str):
	"""Decode token and bind username to this socket session."""
	payload = jwt.decode(token, config.JWT_SECRET, algorithms=['HS256'])
	username = payload['username']
	user = db.users.find_one({'username': username})
	if not user:
		raise ValueError('Invalid user')
	_connected_sid_to_username[request.sid] = username
	socket_session['username'] = username
	return username

def init_socketio(socketio):
	"""Initialize Socket.IO event handlers."""
	
	@socketio.on('connect')
	def handle_connect():
		"""Handle client connection with JWT verification."""
		try:
			# Get token from query parameters
			token = request.args.get('token')
			
			if not token:
				logger.warning("Connection attempt without token")
				emit('system', {'message': 'Authentication required'})
				disconnect()
				return
			
			# Verify JWT token
			try:
				username = _bind_username_from_token(token)
				logger.info(f"User connected: {username} (sid={request.sid})")
				emit('system', {'message': f'Welcome, {username}!'})
				
			except jwt.ExpiredSignatureError:
				logger.warning("Connection attempt with expired token")
				emit('system', {'message': 'Token expired'})
				disconnect()
				return
			except (jwt.InvalidTokenError, ValueError):
				logger.warning("Connection attempt with invalid token or user")
				emit('system', {'message': 'Invalid token'})
				disconnect()
				return
				
		except Exception as e:
			logger.error(f"Connection error: {e}")
			emit('system', {'message': 'Connection error'})
			disconnect()
	
	@socketio.on('authenticate')
	def handle_authenticate(data):
		"""Explicit auth handshake after connect (client sends token)."""
		try:
			token = (data or {}).get('token')
			if not token:
				emit('system', {'message': 'Authentication required'})
				return
			username = _bind_username_from_token(token)
			logger.info(f"Socket authenticated via event: {username} (sid={request.sid})")
			emit('system', {'message': f'Authenticated as {username}'})
		except jwt.ExpiredSignatureError:
			emit('system', {'message': 'Token expired'})
		except (jwt.InvalidTokenError, ValueError):
			emit('system', {'message': 'Invalid token'})
		except Exception as e:
			logger.error(f"Authenticate error: {e}")
			emit('system', {'message': 'Authentication error'})
	
	@socketio.on('send_message')
	def handle_message(data):
		"""Handle incoming chat messages."""
		try:
			username = _get_username_from_context()
			if not username:
				logger.warning(f"send_message without auth (sid={request.sid})")
				emit('system', {'message': 'Not authenticated'})
				return
			
			content = data.get('message', '').strip()
			
			if not content:
				emit('system', {'message': 'Message cannot be empty'})
				return
			
			# Save user message to database
			user_message = {
				'username': username,
				'sender': 'user',
				'content': content,
				'created_at': datetime.datetime.utcnow()
			}
			
			db.messages.insert_one(user_message)
			
			# Emit user message back to client
			emit('message', {
				'sender': 'user',
				'content': content,
				'timestamp': user_message['created_at'].isoformat()
			})
			
			# Generate AI reply
			ai_reply = generate_ai_reply(username)
			
			# Save AI reply to database
			ai_message = {
				'username': username,
				'sender': 'ai',
				'content': ai_reply,
				'created_at': datetime.datetime.utcnow()
			}
			
			db.messages.insert_one(ai_message)
			
			# Emit AI reply to client
			emit('message', {
				'sender': 'ai',
				'content': ai_reply,
				'timestamp': ai_message['created_at'].isoformat()
			})
			
			logger.info(f"Message processed for user: {username}")
			
		except Exception as e:
			logger.error(f"Message handling error: {e}")
			emit('system', {'message': 'Error processing message'})
	
	@socketio.on('disconnect')
	def handle_disconnect():
		"""Handle client disconnection."""
		try:
			username = _connected_sid_to_username.pop(request.sid, None) or socket_session.get('username')
			if username:
				logger.info(f"User disconnected: {username} (sid={request.sid})")
			else:
				logger.info("Anonymous user disconnected")
		except Exception as e:
			logger.error(f"Disconnect error: {e}")



