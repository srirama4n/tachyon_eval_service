from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

    @classmethod
    async def connect_to_database(cls):
        """Create database connection."""
        try:
            cls.client = AsyncIOMotorClient(settings.mongodb_url)
            cls.db = cls.client[settings.mongodb_db_name]
            logger.info(f"Connected to MongoDB at {settings.mongodb_url}")
        except Exception as e:
            logger.error(f"Could not connect to MongoDB: {str(e)}")
            raise

    @classmethod
    async def close_database_connection(cls):
        """Close database connection."""
        if cls.client:
            cls.client.close()
            logger.info("Closed MongoDB connection")

    @classmethod
    def get_db(cls):
        return cls.db 