from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.schemas.dataset import Dataset, DatasetCreate
from app.services.dataset_service import DatasetService
from app.core.exceptions import (
    DatasetValidationError, DatasetNotFoundError,
    DatasetAlreadyExistsError, DatabaseError
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/usecases/{usecase_id}/datasets", response_model=List[Dataset])
async def get_datasets(usecase_id: str):
    try:
        return await DatasetService.get_datasets(usecase_id)
    except DatabaseError as e:
        logger.error(f"Database error in get_datasets: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in get_datasets: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/usecases/{usecase_id}/datasets/{dataset_id}", response_model=Dataset)
async def get_dataset(usecase_id: str, dataset_id: str):
    try:
        return await DatasetService.get_dataset(usecase_id, dataset_id)
    except DatasetNotFoundError as e:
        logger.error(f"Dataset not found in get_dataset: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error in get_dataset: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in get_dataset: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/usecases/{usecase_id}/datasets", response_model=Dataset)
async def create_dataset(usecase_id: str, dataset: DatasetCreate):
    try:
        return await DatasetService.create_dataset(usecase_id, dataset)
    except DatasetValidationError as e:
        logger.error(f"Validation error in create_dataset: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except DatasetAlreadyExistsError as e:
        logger.error(f"Dataset already exists in create_dataset: {str(e)}")
        raise HTTPException(status_code=409, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error in create_dataset: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in create_dataset: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/usecases/{usecase_id}/datasets/{dataset_id}")
async def delete_dataset(usecase_id: str, dataset_id: str):
    try:
        success = await DatasetService.delete_dataset(usecase_id, dataset_id)
        if not success:
            raise DatasetNotFoundError(dataset_id)
        return {"message": f"Dataset {dataset_id} deleted successfully"}
    except DatasetNotFoundError as e:
        logger.error(f"Dataset not found in delete_dataset: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error in delete_dataset: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in delete_dataset: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error") 