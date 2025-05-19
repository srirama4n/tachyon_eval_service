import os
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import logging
from datetime import datetime
from app.core.config import settings
from app.db.mongodb import MongoDB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def setup_database():
    """Set up MongoDB collections and indexes."""
    try:
        # Connect to MongoDB
        await MongoDB.connect_to_database()
        
        # Create collections with schema validation
        db = MongoDB.db
        
        # Create datasets collection
        await db.create_collection("datasets", validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["id", "usecase_id", "name", "alias", "created_at", "updated_at"],
                "properties": {
                    "id": {"bsonType": "string"},
                    "usecase_id": {"bsonType": "string"},
                    "name": {"bsonType": "string"},
                    "alias": {"bsonType": "string"},
                    "description": {"bsonType": "string"},
                    "created_at": {"bsonType": "date"},
                    "updated_at": {"bsonType": "date"}
                }
            }
        })
        
        # Create evaluations collection
        await db.create_collection("evaluations", validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["id", "usecase_id", "dataset_id", "status", "created_at", "updated_at"],
                "properties": {
                    "id": {"bsonType": "string"},
                    "usecase_id": {"bsonType": "string"},
                    "dataset_id": {"bsonType": "string"},
                    "model_version": {"bsonType": "string"},
                    "parameters": {"bsonType": "object"},
                    "status": {"enum": ["pending", "running", "completed", "failed"]},
                    "result": {"bsonType": "object"},
                    "error": {"bsonType": "string"},
                    "created_at": {"bsonType": "date"},
                    "updated_at": {"bsonType": "date"},
                    "completed_at": {"bsonType": "date"},
                    "failed_at": {"bsonType": "date"}
                }
            }
        })
        
        # Create metrics collection
        await db.create_collection("metrics", validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["usecase_id", "name", "value", "timestamp"],
                "properties": {
                    "usecase_id": {"bsonType": "string"},
                    "dataset_id": {"bsonType": "string"},
                    "evaluation_id": {"bsonType": "string"},
                    "name": {"bsonType": "string"},
                    "value": {"bsonType": "double"},
                    "timestamp": {"bsonType": "date"},
                    "confidence_interval": {
                        "bsonType": "object",
                        "properties": {
                            "lower": {"bsonType": "double"},
                            "upper": {"bsonType": "double"}
                        }
                    }
                }
            }
        })
        
        # Create indexes
        await db.datasets.create_index([("usecase_id", 1), ("alias", 1)], unique=True)
        await db.evaluations.create_index([("usecase_id", 1), ("id", 1)], unique=True)
        await db.metrics.create_index([("usecase_id", 1), ("timestamp", 1)])
        await db.metrics.create_index([("dataset_id", 1), ("timestamp", 1)])
        await db.metrics.create_index([("evaluation_id", 1), ("timestamp", 1)])
        
        logger.info("Database setup completed successfully")
        
    except Exception as e:
        logger.error(f"Error setting up database: {str(e)}")
        raise
    finally:
        await MongoDB.close_database_connection()

if __name__ == "__main__":
    asyncio.run(setup_database()) 