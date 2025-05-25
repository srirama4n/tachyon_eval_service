from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional
from models import Dataset, Golden, Usecase
from datetime import datetime
import os
from dotenv import load_dotenv
from exceptions import (
    DatasetNotFoundError,
    DatasetAlreadyExistsError,
    GoldenNotFoundError,
    DatabaseError
)

# Load environment variables from .env file
load_dotenv()

class Database:
    client: AsyncIOMotorClient = None
    db = None

    @classmethod
    async def connect_db(cls):
        try:
            # Get MongoDB connection string and database name from environment variables
            mongodb_url = os.getenv("MONGODB_URL", "mongodb+srv://techsrirama:E18AOxDOPv4Cm83k@cluster0.ug1lhai.mongodb.net/")
            database_name = os.getenv("DATABASE_NAME", "dataset_management")
            
            cls.client = AsyncIOMotorClient(mongodb_url)
            cls.db = cls.client[database_name]
        except Exception as e:
            raise DatabaseError(detail=f"Failed to connect to database: {str(e)}")

    @classmethod
    async def close_db(cls):
        if cls.client:
            try:
                cls.client.close()
            except Exception as e:
                raise DatabaseError(detail=f"Failed to close database connection: {str(e)}")

    @classmethod
    async def get_datasets(cls, usecase_id: str) -> List[Dataset]:
        try:
            cursor = cls.db.datasets.find({"usecase_id": usecase_id})
            datasets = []
            async for document in cursor:
                document["created_at"] = document["created_at"].isoformat()
                document["updated_at"] = document["updated_at"].isoformat()
                datasets.append(Dataset(**document))
            return datasets
        except Exception as e:
            raise DatabaseError(detail=f"Failed to fetch datasets: {str(e)}")

    @classmethod
    async def get_dataset(cls, usecase_id: str, dataset_id: str) -> Dataset:
        try:
            document = await cls.db.datasets.find_one({
                "id": dataset_id,
                "usecase_id": usecase_id
            })
            if not document:
                raise DatasetNotFoundError(dataset_id)
            
            document["created_at"] = document["created_at"].isoformat()
            document["updated_at"] = document["updated_at"].isoformat()
            return Dataset(**document)
        except DatasetNotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(detail=f"Failed to fetch dataset: {str(e)}")

    @classmethod
    async def create_dataset(cls, dataset: Dataset) -> Dataset:
        try:
            # Check if dataset already exists in the same usecase
            existing = await cls.db.datasets.find_one({
                "alias": dataset.alias,
                "usecase_id": dataset.usecase_id
            })
            if existing:
                raise DatasetAlreadyExistsError(dataset.alias)
            
            dataset_dict = dataset.model_dump()
            await cls.db.datasets.insert_one(dataset_dict)
            return dataset
        except DatasetAlreadyExistsError:
            raise
        except Exception as e:
            raise DatabaseError(detail=f"Failed to create dataset: {str(e)}")

    @classmethod
    async def delete_dataset(cls, usecase_id: str, dataset_id: str):
        try:
            # Check if dataset exists
            existing = await cls.db.datasets.find_one({
                "id": dataset_id,
                "usecase_id": usecase_id
            })
            if not existing:
                raise DatasetNotFoundError(dataset_id)
            
            await cls.db.datasets.delete_one({
                "id": dataset_id,
                "usecase_id": usecase_id
            })
            # Also delete all associated goldens
            await cls.db.goldens.delete_many({
                "dataset_id": dataset_id,
                "usecase_id": usecase_id
            })
        except DatasetNotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(detail=f"Failed to delete dataset: {str(e)}")

    @classmethod
    async def get_goldens(cls, usecase_id: str, dataset_id: str) -> List[Golden]:
        try:
            # Check if dataset exists
            existing = await cls.db.datasets.find_one({
                "id": dataset_id,
                "usecase_id": usecase_id
            })
            if not existing:
                raise DatasetNotFoundError(dataset_id)
            
            cursor = cls.db.goldens.find({
                "dataset_id": dataset_id,
                "usecase_id": usecase_id
            })
            goldens = []
            async for document in cursor:
                document["created_at"] = document["created_at"].isoformat()
                document["updated_at"] = document["updated_at"].isoformat()
                goldens.append(Golden(**document))
            return goldens
        except DatasetNotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(detail=f"Failed to fetch goldens: {str(e)}")

    @classmethod
    async def create_golden(cls, golden: Golden) -> Golden:
        try:
            # Check if dataset exists
            existing = await cls.db.datasets.find_one({
                "id": golden.dataset_id,
                "usecase_id": golden.usecase_id
            })
            if not existing:
                raise DatasetNotFoundError(golden.dataset_id)
            
            golden_dict = golden.model_dump()
            await cls.db.goldens.insert_one(golden_dict)
            return golden
        except DatasetNotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(detail=f"Failed to create golden: {str(e)}")

    @classmethod
    async def update_golden(cls, usecase_id: str, golden_id: str, golden_update: Golden) -> Golden:
        try:
            # Check if golden exists
            existing = await cls.db.goldens.find_one({
                "id": golden_id,
                "usecase_id": usecase_id
            })
            if not existing:
                raise GoldenNotFoundError(golden_id)
            
            # Check if dataset exists
            existing_dataset = await cls.db.datasets.find_one({
                "id": golden_update.dataset_id,
                "usecase_id": usecase_id
            })
            if not existing_dataset:
                raise DatasetNotFoundError(golden_update.dataset_id)
            
            golden_dict = golden_update.model_dump()
            golden_dict["updated_at"] = datetime.now()
            await cls.db.goldens.update_one(
                {"id": golden_id, "usecase_id": usecase_id},
                {"$set": golden_dict}
            )
            return golden_update
        except (GoldenNotFoundError, DatasetNotFoundError):
            raise
        except Exception as e:
            raise DatabaseError(detail=f"Failed to update golden: {str(e)}")

    @classmethod
    async def delete_golden(cls, usecase_id: str, golden_id: str):
        try:
            # Check if golden exists
            existing = await cls.db.goldens.find_one({
                "id": golden_id,
                "usecase_id": usecase_id
            })
            if not existing:
                raise GoldenNotFoundError(golden_id)
            
            await cls.db.goldens.delete_one({
                "id": golden_id,
                "usecase_id": usecase_id
            })
        except GoldenNotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(detail=f"Failed to delete golden: {str(e)}")

    @classmethod
    async def import_goldens(cls, goldens_to_import: List[Golden]) -> List[Golden]:
        try:
            if not goldens_to_import:
                return []
            
            # Check if dataset exists
            dataset_id = goldens_to_import[0].dataset_id
            usecase_id = goldens_to_import[0].usecase_id
            existing = await cls.db.datasets.find_one({
                "id": dataset_id,
                "usecase_id": usecase_id
            })
            if not existing:
                raise DatasetNotFoundError(dataset_id)
            
            golden_dicts = [golden.model_dump() for golden in goldens_to_import]
            await cls.db.goldens.insert_many(golden_dicts)
            return goldens_to_import
        except DatasetNotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(detail=f"Failed to import goldens: {str(e)}")

