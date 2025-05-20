from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict
from app.schemas.evaluation import Evaluation, EvaluationCreate, EvaluationUpdate
from app.schemas.evaluation_response import EvaluationResponse
from app.services.evaluation_service import EvaluationService
from app.core.exceptions import (
    EvaluationValidationError, EvaluationNotFoundError,
    DatasetNotFoundError, DatabaseError
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/usecases/{usecase_id}/evaluations", response_model=List[Evaluation])
async def get_evaluations(usecase_id: str):
    try:
        return await EvaluationService.get_evaluations(usecase_id)
    except DatabaseError as e:
        logger.error(f"Database error in get_evaluations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in get_evaluations: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/usecases/{usecase_id}/evaluations/{evaluation_id}", response_model=Evaluation)
async def get_evaluation(usecase_id: str, evaluation_id: str):
    try:
        return await EvaluationService.get_evaluation(usecase_id, evaluation_id)
    except EvaluationNotFoundError as e:
        logger.error(f"Evaluation not found in get_evaluation: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error in get_evaluation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in get_evaluation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/usecases/{usecase_id}/evaluations", response_model=Evaluation)
async def create_evaluation(usecase_id: str, evaluation: EvaluationCreate):
    try:
        # Validate evaluation data
        if not evaluation.dataset_id:
            raise EvaluationValidationError("Dataset ID is required")
        
        if not evaluation.model_id:
            raise EvaluationValidationError("Model Id is required")

        return await EvaluationService.create_evaluation(usecase_id, evaluation)
    except EvaluationValidationError as e:
        logger.error(f"Validation error in create_evaluation: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except DatasetNotFoundError as e:
        logger.error(f"Dataset not found in create_evaluation: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error in create_evaluation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in create_evaluation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/usecases/{usecase_id}/evaluations/{evaluation_id}", response_model=Evaluation)
async def update_evaluation(
    usecase_id: str,
    evaluation_id: str,
    evaluation: EvaluationUpdate
):
    try:
        return await EvaluationService.update_evaluation(usecase_id, evaluation_id, evaluation)
    except EvaluationNotFoundError as e:
        logger.error(f"Evaluation not found in update_evaluation: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except EvaluationValidationError as e:
        logger.error(f"Validation error in update_evaluation: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error in update_evaluation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in update_evaluation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/usecases/{usecase_id}/evaluations/{evaluation_id}")
async def delete_evaluation(usecase_id: str, evaluation_id: str):
    try:
        success = await EvaluationService.delete_evaluation(usecase_id, evaluation_id)
        if not success:
            raise EvaluationNotFoundError(evaluation_id)
        return {"message": f"Evaluation {evaluation_id} deleted successfully"}
    except EvaluationNotFoundError as e:
        logger.error(f"Evaluation not found in delete_evaluation: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error in delete_evaluation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in delete_evaluation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.patch("/usecases/{usecase_id}/evaluations/{evaluation_id}/status", response_model=Evaluation)
async def update_evaluation_status(
    usecase_id: str,
    evaluation_id: str,
    status: str,
    result: Optional[Dict] = None
):
    try:
        return await EvaluationService.update_evaluation_status(
            usecase_id, evaluation_id, status, result
        )
    except EvaluationNotFoundError as e:
        logger.error(f"Evaluation not found in update_evaluation_status: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except EvaluationValidationError as e:
        logger.error(f"Validation error in update_evaluation_status: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error in update_evaluation_status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in update_evaluation_status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error") 
    
@router.get("/usecases/{usecase_id}/evaluations/{evaluation_id}/responses", response_model=List[EvaluationResponse])
async def get_evaluation_responses(evaluation_id: str):
    try:
        return await EvaluationService.get_evaluation_responses(evaluation_id)
    except EvaluationNotFoundError as e:
        logger.error(f"Evaluation not found in get_evaluation_responses: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error in get_evaluation_responses: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in get_evaluation_responses: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")