from pydantic import BaseModel
from datetime import datetime
import uuid

class DatasetBase(BaseModel):
    alias: str
    

class DatasetCreate(DatasetBase):
    pass

class Dataset(DatasetBase):
    id: str = str(uuid.uuid4())
    usecase_id: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    class Config:
        from_attributes = True 