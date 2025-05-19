from typing import List, Optional, Dict
from datetime import datetime, UTC
import uuid
from app.db.mongodb import MongoDB
from app.schemas.evaluation import Evaluation, EvaluationCreate, EvaluationUpdate
from app.core.exceptions import (
    EvaluationNotFoundError, EvaluationValidationError,
    DatasetNotFoundError, DatabaseError
)
from app.core.retry import with_retry
import logging
from pymongo.errors import ServerSelectionTimeoutError, OperationFailure

logger = logging.getLogger(__name__)

class EvaluationService:
    @staticmethod
    @with_retry(
        max_retries=3,
        initial_delay=1.0,
        max_delay=10.0,
        exceptions=(ServerSelectionTimeoutError, OperationFailure)
    )
    async def get_evaluations(
        usecase_id: str) -> List[Evaluation]:
        try:
            query = {"usecase_id": usecase_id}

            evaluations = await MongoDB.db.evaluations.find(query).to_list(None)
            return [Evaluation(**evaluation) for evaluation in evaluations]
        except Exception as e:
            logger.error(f"Error getting evaluations: {str(e)}")
            raise DatabaseError(f"Failed to get evaluations: {str(e)}")

    @staticmethod
    @with_retry(
        max_retries=3,
        initial_delay=1.0,
        max_delay=10.0,
        exceptions=(ServerSelectionTimeoutError, OperationFailure)
    )
    async def get_evaluation(usecase_id: str, evaluation_id: str) -> Evaluation:
        try:
            evaluation = await MongoDB.db.evaluations.find_one({
                "id": evaluation_id,
                "usecase_id": usecase_id
            })
            if not evaluation:
                raise EvaluationNotFoundError(evaluation_id)
            return Evaluation(**evaluation)
        except EvaluationNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error getting evaluation: {str(e)}")
            raise DatabaseError(f"Failed to get evaluation: {str(e)}")

    @staticmethod
    @with_retry(
        max_retries=3,
        initial_delay=1.0,
        max_delay=10.0,
        exceptions=(ServerSelectionTimeoutError, OperationFailure)
    )
    async def create_evaluation(usecase_id: str, evaluation: EvaluationCreate) -> Evaluation:
        try:
            print({
                "id": evaluation.dataset_id,
                "usecase_id": usecase_id
            })
            # Verify dataset exists
            dataset = await MongoDB.db.datasets.find_one({
                "id": evaluation.dataset_id,
                "usecase_id": usecase_id
            })
            if not dataset:
                raise DatasetNotFoundError(evaluation.dataset_id)

            # Create evaluation
            evaluation_dict = evaluation.model_dump()
            evaluation_dict["id"] = str(uuid.uuid4())
            evaluation_dict["usecase_id"] = usecase_id
            evaluation_dict["status"] = "pending"
            evaluation_dict["created_at"] = datetime.now(UTC)
            evaluation_dict["updated_at"] = datetime.now(UTC)
            
            result = await MongoDB.db.evaluations.insert_one(evaluation_dict)
            
            # Get created evaluation
            created_evaluation = await MongoDB.db.evaluations.find_one({"_id": result.inserted_id})
            return Evaluation(**created_evaluation)
        except DatasetNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error creating evaluation: {str(e)}")
            raise DatabaseError(f"Failed to create evaluation: {str(e)}")

    @staticmethod
    @with_retry(
        max_retries=3,
        initial_delay=1.0,
        max_delay=10.0,
        exceptions=(ServerSelectionTimeoutError, OperationFailure)
    )
    async def update_evaluation(
        usecase_id: str,
        evaluation_id: str,
        evaluation: EvaluationUpdate
    ) -> Evaluation:
        try:
            # Check if evaluation exists
            existing = await MongoDB.db.evaluations.find_one({
                "id": evaluation_id,
                "usecase_id": usecase_id
            })
            if not existing:
                raise EvaluationNotFoundError(evaluation_id)

            # Validate dataset if being updated
            if evaluation.dataset_id:
                dataset = await MongoDB.db.datasets.find_one({
                    "id": evaluation.dataset_id,
                    "usecase_id": usecase_id
                })
                if not dataset:
                    raise DatasetNotFoundError(evaluation.dataset_id)

            # Update evaluation
            update_data = evaluation.dict(exclude_unset=True)
            update_data["updated_at"] = datetime.now(UTC)
            
            await MongoDB.db.evaluations.update_one(
                {"id": evaluation_id, "usecase_id": usecase_id},
                {"$set": update_data}
            )
            
            # Get updated evaluation
            updated_evaluation = await MongoDB.db.evaluations.find_one({
                "id": evaluation_id,
                "usecase_id": usecase_id
            })
            return Evaluation(**updated_evaluation)
        except (EvaluationNotFoundError, DatasetNotFoundError):
            raise
        except Exception as e:
            logger.error(f"Error updating evaluation: {str(e)}")
            raise DatabaseError(f"Failed to update evaluation: {str(e)}")

    @staticmethod
    @with_retry(
        max_retries=3,
        initial_delay=1.0,
        max_delay=10.0,
        exceptions=(ServerSelectionTimeoutError, OperationFailure)
    )
    async def delete_evaluation(usecase_id: str, evaluation_id: str) -> bool:
        try:
            # Check if evaluation exists
            evaluation = await MongoDB.db.evaluations.find_one({
                "id": evaluation_id,
                "usecase_id": usecase_id
            })
            if not evaluation:
                raise EvaluationNotFoundError(evaluation_id)

            # Delete evaluation
            result = await MongoDB.db.evaluations.delete_one({
                "id": evaluation_id,
                "usecase_id": usecase_id
            })
            return result.deleted_count > 0
        except EvaluationNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error deleting evaluation: {str(e)}")
            raise DatabaseError(f"Failed to delete evaluation: {str(e)}")

    @staticmethod
    @with_retry(
        max_retries=3,
        initial_delay=1.0,
        max_delay=10.0,
        exceptions=(ServerSelectionTimeoutError, OperationFailure)
    )
    async def update_evaluation_status(
        usecase_id: str,
        evaluation_id: str,
        status: str
    ) -> Evaluation:
        try:
            # Validate status
            valid_statuses = ["pending", "running", "completed", "failed"]
            if status not in valid_statuses:
                raise EvaluationValidationError(f"Invalid status: {status}. Must be one of {valid_statuses}")

            # Check if evaluation exists
            evaluation = await MongoDB.db.evaluations.find_one({
                "id": evaluation_id,
                "usecase_id": usecase_id
            })
            if not evaluation:
                raise EvaluationNotFoundError(evaluation_id)

            # Update status
            update_data = {
                "status": status,
                "updated_at": datetime.now(UTC)
            }
            
            if status == "completed":
                update_data["completed_at"] = datetime.now(UTC)
            elif status == "failed":
                update_data["failed_at"] = datetime.now(UTC)

            await MongoDB.db.evaluations.update_one(
                {"id": evaluation_id, "usecase_id": usecase_id},
                {"$set": update_data}
            )
            
            # Get updated evaluation
            updated_evaluation = await MongoDB.db.evaluations.find_one({
                "id": evaluation_id,
                "usecase_id": usecase_id
            })
            return Evaluation(**updated_evaluation)
        except (EvaluationNotFoundError, EvaluationValidationError):
            raise
        except Exception as e:
            logger.error(f"Error updating evaluation status: {str(e)}")
            raise DatabaseError(f"Failed to update evaluation status: {str(e)}") 