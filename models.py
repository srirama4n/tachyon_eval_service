from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

class Dataset(BaseModel):
    id: str = str(uuid.uuid4())
    alias: str
    usecase_id: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class Golden(BaseModel):
    id: str = str(uuid.uuid4())
    usecase_id: str
    dataset_id: str
    input: str
    output: str
    metadata: Optional[dict] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now() 