from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
import uuid

class GoldenBase(BaseModel):
    input: str
    actualOutput: Optional[str] = None
    expectedOutput: str
    context: str
    retrievalContext: Optional[str] = None


class GoldenCreate(GoldenBase):
    pass

class GoldenUpdate(BaseModel):
    input: Optional[str] = None
    actualOutput: Optional[str] = None
    expectedOutput: Optional[str] = None
    context: Optional[str] = None
    retrievalContext: Optional[str] = None

class GoldenGenerate(GoldenBase):
    count: int
    tags: List[str]

class GoldenImport(BaseModel):
    input: str
    actualOutput: str = ""
    expectedOutput: str
    context: str
    retrievalContext: str

class Golden(GoldenUpdate):
    id: str = str(uuid.uuid4())
    dataset_id: str
    usecase_id: str

    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    class Config:
        from_attributes = True 