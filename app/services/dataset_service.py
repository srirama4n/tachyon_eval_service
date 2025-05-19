from typing import List, Optional
from datetime import datetime, UTC
from app.db.mongodb import MongoDB
from app.schemas.dataset import Dataset, DatasetCreate
from app.core.exceptions import (
    DatasetNotFoundError, DatasetAlreadyExistsError,
    DatasetValidationError, DatabaseError
)
from app.core.retry import with_retry
import logging
from pymongo.errors import ServerSelectionTimeoutError, OperationFailure

logger = logging.getLogger(__name__)

class DatasetService:
    @staticmethod
    @with_retry(
        max_retries=3,
        initial_delay=1.0,
        max_delay=10.0,
        exceptions=(ServerSelectionTimeoutError, OperationFailure)
    )
    async def get_datasets(usecase_id: str) -> List[Dataset]:
        try:
            datasets = await MongoDB.db.datasets.find({"usecase_id": usecase_id}).to_list(None)
            return [Dataset(**dataset) for dataset in datasets]
        except Exception as e:
            logger.error(f"Error getting datasets: {str(e)}")
            raise DatabaseError(f"Failed to get datasets: {str(e)}")

    @staticmethod
    @with_retry(
        max_retries=3,
        initial_delay=1.0,
        max_delay=10.0,
        exceptions=(ServerSelectionTimeoutError, OperationFailure)
    )
    async def get_dataset(usecase_id: str, dataset_id: str) -> Dataset:
        try:
            dataset = await MongoDB.db.datasets.find_one({
                "id": dataset_id,
                "usecase_id": usecase_id
            })
            if not dataset:
                raise DatasetNotFoundError(dataset_id)
            return Dataset(**dataset)
        except DatasetNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error getting dataset: {str(e)}")
            raise DatabaseError(f"Failed to get dataset: {str(e)}")

    @staticmethod
    @with_retry(
        max_retries=3,
        initial_delay=1.0,
        max_delay=10.0,
        exceptions=(ServerSelectionTimeoutError, OperationFailure)
    )
    async def create_dataset(usecase_id: str, dataset: DatasetCreate) -> Dataset:
        try:
            # Check if dataset with same alias exists in the usecase
            existing_dataset = await MongoDB.db.datasets.find_one({
                "usecase_id": usecase_id,
                "alias": dataset.alias
            })
            if existing_dataset:
                raise DatasetAlreadyExistsError(dataset.alias)

            # Create new dataset using Dataset POJO
            new_dataset = Dataset(
                **dataset.model_dump(),
                usecase_id=usecase_id,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC)
            )
            
            # Insert into database
            await MongoDB.db.datasets.insert_one(new_dataset.model_dump())
            
            return new_dataset
        except DatasetAlreadyExistsError:
            raise
        except Exception as e:
            logger.error(f"Error creating dataset: {str(e)}")
            raise DatabaseError(f"Failed to create dataset: {str(e)}")

    @staticmethod
    @with_retry(
        max_retries=3,
        initial_delay=1.0,
        max_delay=10.0,
        exceptions=(ServerSelectionTimeoutError, OperationFailure)
    )
    async def delete_dataset(usecase_id: str, dataset_id: str) -> bool:
        try:
            # Check if dataset exists
            dataset = await MongoDB.db.datasets.find_one({
                "id": dataset_id,
                "usecase_id": usecase_id
            })
            if not dataset:
                raise DatasetNotFoundError(dataset_id)

            # Delete dataset
            result = await MongoDB.db.datasets.delete_one({
                "id": dataset_id,
                "usecase_id": usecase_id
            })
            return result.deleted_count > 0
        except DatasetNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error deleting dataset: {str(e)}")
            raise DatabaseError(f"Failed to delete dataset: {str(e)}") 