from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class MetricData(BaseModel):
    name: str
    threshold: float
    success: bool
    score: float
    reason: str
    strictMode: bool
    evaluationModel: str
    verboseLogs: str = ""

class ResponseData(BaseModel):
    name: str
    input: str
    actualoutput: str
    expectedOutput: str
    context: List[str]
    retrievalContext: List[str]
    success: bool
    metricsData: List[MetricData]
    runDuration: float
    order: int

class EvaluationResponse(BaseModel):
    id: str
    evaluation_id: str
    evaluation_name: str
    dataset_id: str
    model_id: str
    usecase_id: str
    status: str
    created_at: datetime
    data: ResponseData 