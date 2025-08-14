import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class that loads settings from environment variables."""
    
    # MongoDB Configuration
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/nexuschat')
    
    # JWT Configuration
    JWT_SECRET = os.getenv('JWT_SECRET', 'please-change-me')
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    
    # Gemini Configuration (fallback)
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
    
    # Server Configuration
    PORT = int(os.getenv('PORT', 5000))
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', JWT_SECRET)
    DEBUG = os.getenv('FLASK_ENV') == 'development'

# Global config instance
config = Config()



