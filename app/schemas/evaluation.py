from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Optional, Any
import uuid

class TestParameter(BaseModel):
    name: str
    value: str

class EvaluationBase(BaseModel):
    evaluation_name: str
    dataset_id: str
    model_id: str
    temperature: str
    parameters: List[TestParameter]
    

class Parameter(BaseModel):
    name: str
    value: str

class EvaluationCreate(EvaluationBase):
    pass

class EvaluationUpdate(BaseModel):
    dataset_id: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class Evaluation(EvaluationCreate):
    id: str
    dataset_id: str
    usecase_id: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    completed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    class Config:
        from_attributes = True 