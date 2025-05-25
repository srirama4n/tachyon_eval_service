from typing import List, Optional
from datetime import datetime, UTC
import uuid
from app.db.mongodb import MongoDB
from app.schemas.usecase import Usecase, UsecaseCreate, UsecaseUpdate
from app.core.exceptions import UsecaseNotFoundError, DatabaseError, UsecaseValidationError
from app.core.retry import with_retry
import logging
from pymongo.errors import ServerSelectionTimeoutError, OperationFailure

logger = logging.getLogger(__name__)

class UsecaseService:
    @staticmethod
    @with_retry(
        max_retries=3,
        initial_delay=1.0,
        max_delay=10.0,
        exceptions=(ServerSelectionTimeoutError, OperationFailure)
    )
    async def get_usecase(usecase_id: str) -> Usecase:
        try:
            usecase = await MongoDB.db.usecases.find_one({"id": usecase_id})
            if not usecase:
                raise UsecaseNotFoundError(usecase_id)
            return Usecase(**usecase)
        except UsecaseNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error getting usecase: {str(e)}")
            raise DatabaseError(f"Failed to get usecase: {str(e)}")

    @staticmethod
    @with_retry(
        max_retries=3,
        initial_delay=1.0,
        max_delay=10.0,
        exceptions=(ServerSelectionTimeoutError, OperationFailure)
    )
    async def create_usecase(usecase_data: UsecaseCreate) -> Usecase:
        try:
            # Validate required fields
            required_fields = ['model_id', 'onboarded_to', 'authentication']
            missing_fields = [field for field in required_fields if field not in usecase_data]
            if missing_fields:
                raise UsecaseValidationError(f"Missing required fields: {', '.join(missing_fields)}")

            # Create usecase with timestamps
            usecase_dict = {
                **usecase_data,
                "id": str(uuid.uuid4()),
                "created_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC)
            }
            
            # Check if usecase already exists
            existing = await MongoDB.db.usecases.find_one({"id": usecase_dict["id"]})
            if existing:
                raise UsecaseValidationError(f"Usecase with id {usecase_dict['id']} already exists")
            
            # Insert into database
            await MongoDB.db.usecases.insert_one(usecase_dict)
            
            return Usecase(**usecase_dict)
        except UsecaseValidationError:
            raise
        except Exception as e:
            logger.error(f"Error creating usecase: {str(e)}")
            raise DatabaseError(f"Failed to create usecase: {str(e)}")

    @staticmethod
    @with_retry(
        max_retries=3,
        initial_delay=1.0,
        max_delay=10.0,
        exceptions=(ServerSelectionTimeoutError, OperationFailure)
    )
    async def update_usecase(usecase_id: str, usecase_data: UsecaseUpdate) -> Usecase:
        try:
            # Check if usecase exists
            existing = await MongoDB.db.usecases.find_one({"id": usecase_id})
            if not existing:
                raise UsecaseNotFoundError(usecase_id)
            
            # Validate required fields
            required_fields = ['model_id', 'onboarded_to', 'authentication']
            missing_fields = [field for field in required_fields if field not in usecase_data]
            if missing_fields:
                raise UsecaseValidationError(f"Missing required fields: {', '.join(missing_fields)}")
            
            # Update usecase with timestamps
            update_data = {
                **usecase_data,
                "updated_at": datetime.now(UTC)
            }
            
            await MongoDB.db.usecases.update_one(
                {"id": usecase_id},
                {"$set": update_data}
            )
            
            # Get updated usecase
            updated_usecase = await MongoDB.db.usecases.find_one({"id": usecase_id})
            return Usecase(**updated_usecase)
        except (UsecaseNotFoundError, UsecaseValidationError):
            raise
        except Exception as e:
            logger.error(f"Error updating usecase: {str(e)}")
            raise DatabaseError(f"Failed to update usecase: {str(e)}")

    @staticmethod
    @with_retry(
        max_retries=3,
        initial_delay=1.0,
        max_delay=10.0,
        exceptions=(ServerSelectionTimeoutError, OperationFailure)
    )
    async def delete_usecase(usecase_id: str) -> bool:
        try:
            # Check if usecase exists
            usecase = await MongoDB.db.usecases.find_one({"id": usecase_id})
            if not usecase:
                raise UsecaseNotFoundError(usecase_id)
            
            # Delete usecase
            result = await MongoDB.db.usecases.delete_one({"id": usecase_id})
            return result.deleted_count > 0
        except UsecaseNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error deleting usecase: {str(e)}")
            raise DatabaseError(f"Failed to delete usecase: {str(e)}") 