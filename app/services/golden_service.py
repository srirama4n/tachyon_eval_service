from typing import List, Optional
from datetime import datetime, UTC
import uuid
from app.db.mongodb import MongoDB
from app.schemas.golden import Golden, GoldenCreate, GoldenImport, GoldenGenerate, GoldenUpdate
from app.core.exceptions import GoldenNotFoundError, GoldenValidationError, DatabaseError
from app.core.retry import with_retry
import logging
from pymongo.errors import ServerSelectionTimeoutError, OperationFailure
import random
import json

logger = logging.getLogger(__name__)

class GoldenService:
    @staticmethod
    async def get_goldens(usecase_id: str, dataset_id: str) -> List[Golden]:
        logger.debug(f"Getting goldens for usecase {usecase_id} and dataset {dataset_id}")
        
        # Breakpoint 1: Check dataset existence
        existing = await MongoDB.db.datasets.find_one({
            "id": dataset_id,
            "usecase_id": usecase_id
        })
        logger.debug(f"Dataset check result: {existing}")
        if not existing:
            raise GoldenValidationError(f"Dataset {dataset_id} not found")
        
        # Breakpoint 2: Query goldens
        cursor = MongoDB.db.goldens.find({
            "dataset_id": dataset_id,
            "usecase_id": usecase_id
        })

        
        goldens = []
        try:
            async for document in cursor:
                logger.debug(f"Raw document from cursor: {document}")
                try:
                    # Convert datetime objects to ISO format strings
                    if "created_at" in document and isinstance(document["created_at"], datetime):
                        document["created_at"] = document["created_at"].isoformat()
                    if "updated_at" in document and isinstance(document["updated_at"], datetime):
                        document["updated_at"] = document["updated_at"].isoformat()
                    
                    logger.debug(f"Processed document: {document}")
                    golden = Golden(**document)
                    logger.debug(f"Created Golden object: {golden}")
                    goldens.append(golden)
                except Exception as e:
                    logger.error(f"Error processing document: {str(e)}")
                    logger.error(f"Problematic document: {document}")
                    continue
        except Exception as e:
            logger.error(f"Error iterating cursor: {str(e)}")
            raise DatabaseError(f"Failed to process goldens: {str(e)}")
        
        logger.debug(f"Returning {len(goldens)} goldens")
        return goldens

    @staticmethod
    async def create_golden(golden: GoldenCreate) -> Golden:
        existing = await MongoDB.db.datasets.find_one({
            "id": golden.dataset_id,
            "usecase_id": golden.usecase_id
        })
        if not existing:
            raise GoldenValidationError(f"Dataset {golden.dataset_id} not found")
        
        new_golden = Golden(**golden.model_dump())
        await MongoDB.db.goldens.insert_one(new_golden.model_dump())
        return new_golden

    @staticmethod
    async def update_golden(usecase_id: str, dataset_id: str, golden_id: str, golden_update: GoldenUpdate) -> Golden:
        existing = await MongoDB.db.goldens.find_one({
            "id": golden_id,
            "usecase_id": usecase_id
        })
        if not existing:
            raise GoldenNotFoundError(golden_id)
        
        existing_dataset = await MongoDB.db.datasets.find_one({
            "id": dataset_id,
            "usecase_id": usecase_id
        })
        if not existing_dataset:
            raise GoldenValidationError(f"Dataset {dataset_id} not found")
        
        # Merge existing data with updates
        update_data = golden_update.model_dump(exclude_unset=True)
        updated_data = {**existing, **update_data, "updated_at": datetime.now(UTC)}
        
        try:
            await MongoDB.db.goldens.update_one(
                {"id": golden_id, "usecase_id": usecase_id},
                {"$set": updated_data}
            )
            return Golden(**updated_data)
        except Exception as e:
            logger.error(f"Error updating golden {golden_id}: {str(e)}")
            raise DatabaseError(f"Failed to update golden: {str(e)}")

    @staticmethod
    async def delete_golden(usecase_id: str, golden_id: str):
        existing = await MongoDB.db.goldens.find_one({
            "id": golden_id,
            "usecase_id": usecase_id
        })
        if not existing:
            raise GoldenNotFoundError(golden_id)
        
        await MongoDB.db.goldens.delete_one({
            "id": golden_id,
            "usecase_id": usecase_id
        })

    @staticmethod
    async def import_goldens(usecase_id: str, dataset_id: str, goldens_to_import: List[GoldenImport]) -> List[Golden]:
        if not goldens_to_import:
            return []
        
        # Verify dataset exists
        existing = await MongoDB.db.datasets.find_one({
            "id": dataset_id,
            "usecase_id": usecase_id
        })
        if not existing:
            raise GoldenValidationError(f"Dataset {dataset_id} not found")

        new_goldens = []
        
        
        now = datetime.now(UTC)
        
        for g in goldens_to_import:
            golden = {
                "id": str(uuid.uuid4()),
                "dataset_id": dataset_id,
                "usecase_id": usecase_id,
                "input": g.input,
                "actualOutput": g.actualOutput,
                "expectedOutput": g.expectedOutput,
                "context": g.context,
                "created_at": now,
                "updated_at": now
            }
            new_goldens.append(golden)
        
        try:
            result = await MongoDB.db.goldens.insert_many(new_goldens)
            logger.info(f"Imported {len(result.inserted_ids)} goldens for dataset {dataset_id}")
            return [Golden(**golden) for golden in new_goldens]
        except Exception as e:
            logger.error(f"Error importing goldens: {str(e)}")
            raise DatabaseError(f"Failed to import goldens: {str(e)}")

    @staticmethod
    @with_retry(
        max_retries=3,
        initial_delay=1.0,
        max_delay=10.0,
        exceptions=(ServerSelectionTimeoutError, OperationFailure)
    )
    async def generate_goldens(
        usecase_id: str,
        dataset_id: str,
        golden: GoldenGenerate
    ) -> List[Golden]:
        try:
            # Verify dataset exists
            dataset = await MongoDB.db.datasets.find_one({
                "id": dataset_id,
                "usecase_id": usecase_id
            })
            if not dataset:
                raise GoldenValidationError(f"Dataset {dataset_id} not found")

            # Generate goldens
            goldens = []
            now = datetime.now(UTC)
            default_tags = ["test", "generated", "sample", "qa", "validation"]
            available_tags = golden.tags if golden.tags else default_tags
            
            for i in range(golden.count):
                new_golden = {
                    "id": str(uuid.uuid4()),
                    "dataset_id": dataset_id,
                    "usecase_id": usecase_id,
                    "input": f"{golden.input } {i+1} about {dataset_id}",
                    "actualOutput": "",
                    "expectedOutput": f"{golden.expectedOutput} for question {i+1}",
                    "context": f"{golden.context} for question {i+1}",
                    "created_at": now,
                    "updated_at": now
                }
                goldens.append(new_golden)

            response = []
            # Insert goldens with error handling
            if goldens:
                try:
                    result = await MongoDB.db.goldens.insert_many(goldens)
                    logger.info(f"Generated {len(result.inserted_ids)} goldens for dataset {dataset_id}")
                    response = [Golden(**golden) for golden in goldens]
                except Exception as e:
                    logger.error(f"Error inserting goldens: {str(e)}")
                    raise DatabaseError(f"Failed to insert generated goldens: {str(e)}")
            
            return response

        except GoldenValidationError:
            raise
        except Exception as e:
            logger.error(f"Error generating goldens: {str(e)}")
            raise DatabaseError(f"Failed to generate goldens: {str(e)}") 