from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from .config import config
import logging

logger = logging.getLogger(__name__)

class Database:
    """MongoDB database connection and setup."""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.users = None
        self.messages = None
    
    def connect(self):
        """Connect to MongoDB and setup collections with indexes."""
        try:
            self.client = MongoClient(config.MONGODB_URI, serverSelectionTimeoutMS=5000)
            # Test the connection
            self.client.admin.command('ping')
            
            self.db = self.client.nexuschat
            self.users = self.db.users
            self.messages = self.db.messages
            
            # Create indexes
            self._create_indexes()
            
            logger.info("Successfully connected to MongoDB")
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
    
    def _create_indexes(self):
        """Create necessary indexes for performance."""
        # Users collection indexes
        self.users.create_index([("username", ASCENDING)], unique=True)
        self.users.create_index([("created_at", DESCENDING)])
        
        # Messages collection indexes
        self.messages.create_index([("username", ASCENDING)])
        self.messages.create_index([("created_at", DESCENDING)])
        self.messages.create_index([("username", ASCENDING), ("created_at", DESCENDING)])
    
    def close(self):
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

# Global database instance
db = Database()



