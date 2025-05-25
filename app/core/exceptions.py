from fastapi import HTTPException, status
from typing import Any, Dict, Optional

class DatasetError(HTTPException):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(status_code=status_code, detail=detail)

class DatasetNotFoundError(DatasetError):
    def __init__(self, dataset_id: str):
        super().__init__(detail=f"Dataset '{dataset_id}' not found", status_code=404)

class DatasetAlreadyExistsError(DatasetError):
    def __init__(self, alias: str):
        super().__init__(detail=f"Dataset with alias '{alias}' already exists", status_code=409)

class GoldenError(HTTPException):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(status_code=status_code, detail=detail)

class GoldenNotFoundError(GoldenError):
    def __init__(self, golden_id: str):
        super().__init__(detail=f"Golden '{golden_id}' not found", status_code=404)

class GoldenValidationError(GoldenError):
    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=400)

class EvaluationError(HTTPException):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(status_code=status_code, detail=detail)

class EvaluationNotFoundError(EvaluationError):
    def __init__(self, evaluation_id: str):
        super().__init__(detail=f"Evaluation '{evaluation_id}' not found", status_code=404)

class EvaluationValidationError(EvaluationError):
    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=400)

class MetricsError(HTTPException):
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(status_code=status_code, detail=detail)

class MetricsNotFoundError(MetricsError):
    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=404)

class MetricsValidationError(MetricsError):
    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=400)

class DatabaseError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=500, detail=detail)

class DatasetValidationError(Exception):
    """Exception raised for dataset validation errors."""
    pass

class UsecaseError(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)

class UsecaseNotFoundError(UsecaseError):
    def __init__(self, usecase_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usecase with id '{usecase_id}' not found"
        )

class UsecaseValidationError(UsecaseError):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        ) 