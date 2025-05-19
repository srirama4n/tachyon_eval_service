from fastapi import HTTPException, status
from typing import Any, Dict, Optional

class DatasetError(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)

class DatasetNotFoundError(DatasetError):
    def __init__(self, alias: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset with alias '{alias}' not found"
        )

class DatasetAlreadyExistsError(DatasetError):
    def __init__(self, alias: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dataset with alias '{alias}' already exists"
        )

class GoldenError(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)

class GoldenNotFoundError(GoldenError):
    def __init__(self, golden_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Golden with ID '{golden_id}' not found"
        )

class GoldenValidationError(GoldenError):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )

class DatabaseError(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: str = "Database operation failed",
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers) 