from flask import Flask, render_template
from flask_cors import CORS
from flask_socketio import SocketIO
import logging
from nexuschat.config import config
from nexuschat.database import db
from nexuschat.auth import auth_bp
from nexuschat.sockets import init_socketio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configure Flask app
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['DEBUG'] = config.DEBUG
    
    # Initialize CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Initialize SocketIO (manage_session ensures per-socket session persistence)
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet', manage_session=True)
    
    # Initialize database
    if not db.connect():
        logger.error("Failed to connect to database")
        return None
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    
    # Initialize Socket.IO event handlers
    init_socketio(socketio)
    
    @app.route('/')
    def index():
        """Serve the main chat interface."""
        return render_template('index.html')
    
    @app.route('/health')
    def health():
        """Health check endpoint."""
        return {'status': 'healthy', 'database': 'connected'}
    
    return app, socketio

def main():
    """Main application entry point."""
    app, socketio = create_app()
    
    if app is None:
        logger.error("Failed to create application")
        return
    
    logger.info(f"Starting NexusChat server on port {config.PORT}")
    logger.info(f"OpenAI Model: {config.OPENAI_MODEL}")
    
    try:
        # Run with SocketIO
        socketio.run(
            app,
            host='0.0.0.0',
            port=config.PORT,
            debug=config.DEBUG,
            use_reloader=False
        )
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        db.close()

if __name__ == '__main__':
    main()



