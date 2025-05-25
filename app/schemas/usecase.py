from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

class UsecaseBase(BaseModel):
    model_id: str = Field(..., description="ID of the model associated with this usecase")
    onboarded_to: str = Field(..., description="Platform or service where the usecase is onboarded")
    authentication: Dict[str, Any] = Field(..., description="Authentication details for the usecase")
    description: Optional[str] = Field(None, description="Optional description of the usecase")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for the usecase")
    status: Optional[str] = Field("active", description="Status of the usecase (active, inactive, etc.)")

class UsecaseCreate(UsecaseBase):
    """Schema for creating a new usecase"""
    pass

class UsecaseUpdate(BaseModel):
    """Schema for updating an existing usecase"""
    model_id: Optional[str] = Field(None, description="ID of the model associated with this usecase")
    onboarded_to: Optional[str] = Field(None, description="Platform or service where the usecase is onboarded")
    authentication: Optional[Dict[str, Any]] = Field(None, description="Authentication details for the usecase")
    description: Optional[str] = Field(None, description="Optional description of the usecase")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for the usecase")
    status: Optional[str] = Field(None, description="Status of the usecase (active, inactive, etc.)")

class Usecase(UsecaseBase):
    """Schema for usecase response"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the usecase")
    created_at: datetime = Field(default_factory=datetime.now, description="Timestamp when the usecase was created")
    updated_at: datetime = Field(default_factory=datetime.now, description="Timestamp when the usecase was last updated")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "model_id": "gpt-4",
                "onboarded_to": "openai",
                "authentication": {
                    "api_key": "sk-...",
                    "organization": "org-..."
                },
                "description": "Example usecase for testing",
                "metadata": {
                    "version": "1.0",
                    "environment": "production"
                },
                "status": "active",
                "created_at": "2024-03-20T10:00:00Z",
                "updated_at": "2024-03-20T10:00:00Z"
            }
        } 