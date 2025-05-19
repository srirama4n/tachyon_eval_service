import asyncio
import logging
from app.db.mongodb import MongoDB
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def setup_database():
    try:
        # Connect to MongoDB
        await MongoDB.connect()
        logger.info("Connected to MongoDB")

        # Create collections if they don't exist
        collections = ["datasets", "goldens", "evaluations", "metrics"]
        for collection in collections:
            if collection not in await MongoDB.db.list_collection_names():
                await MongoDB.db.create_collection(collection)
                logger.info(f"Created collection: {collection}")

        # Create indexes
        # Datasets collection
        await MongoDB.db.datasets.create_index([("id", 1), ("usecase_id", 1)], unique=True)
        await MongoDB.db.datasets.create_index([("usecase_id", 1)])
        
        # Goldens collection
        await MongoDB.db.goldens.create_index([("id", 1), ("usecase_id", 1)], unique=True)
        await MongoDB.db.goldens.create_index([("dataset_id", 1), ("usecase_id", 1)])
        
        # Evaluations collection
        await MongoDB.db.evaluations.create_index([("id", 1), ("usecase_id", 1)], unique=True)
        await MongoDB.db.evaluations.create_index([("dataset_id", 1), ("usecase_id", 1)])
        await MongoDB.db.evaluations.create_index([("status", 1)])
        
        # Metrics collection
        await MongoDB.db.metrics.create_index([("usecase_id", 1), ("timestamp", -1)])
        await MongoDB.db.metrics.create_index([("dataset_id", 1), ("timestamp", -1)])
        await MongoDB.db.metrics.create_index([("evaluation_id", 1), ("timestamp", -1)])

        logger.info("Database setup completed successfully")
    except Exception as e:
        logger.error(f"Error setting up database: {str(e)}")
        raise
    finally:
        await MongoDB.close()

if __name__ == "__main__":
    asyncio.run(setup_database()) 