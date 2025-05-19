from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api import datasets, evaluations, metrics, goldens
from app.core.config import settings
from app.db.mongodb import MongoDB
from app.core.exceptions import (
    DatasetError, DatasetNotFoundError, DatasetAlreadyExistsError,
    DatasetValidationError, EvaluationError, EvaluationNotFoundError,
    EvaluationValidationError, MetricsError, MetricsNotFoundError,
    MetricsValidationError, DatabaseError
)
import logging
import uvicorn
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format=settings.log_format
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app):
    await MongoDB.connect_to_database()
    yield
    await MongoDB.close_database_connection()

app = FastAPI(
    title="Tachyon Evaluation Service",
    description="API for managing datasets and evaluations",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(datasets.router, prefix="/api/v1", tags=["datasets"])
app.include_router(goldens.router, prefix="/api/v1", tags=["goldens"])
app.include_router(evaluations.router, prefix="/api/v1", tags=["evaluations"])
app.include_router(metrics.router, prefix="/api/v1", tags=["metrics"])

# Exception handlers
@app.exception_handler(DatasetError)
async def dataset_error_handler(request: Request, exc: DatasetError):
    logger.error(f"Dataset error: {str(exc)}")
    return {"error": str(exc)}

@app.exception_handler(DatasetNotFoundError)
async def dataset_not_found_handler(request: Request, exc: DatasetNotFoundError):
    logger.error(f"Dataset not found: {str(exc)}")
    return {"error": str(exc)}

@app.exception_handler(DatasetAlreadyExistsError)
async def dataset_already_exists_handler(request: Request, exc: DatasetAlreadyExistsError):
    logger.error(f"Dataset already exists: {str(exc)}")
    return {"error": str(exc)}

@app.exception_handler(DatasetValidationError)
async def dataset_validation_handler(request: Request, exc: DatasetValidationError):
    logger.error(f"Dataset validation error: {str(exc)}")
    return {"error": str(exc)}

@app.exception_handler(EvaluationError)
async def evaluation_error_handler(request: Request, exc: EvaluationError):
    logger.error(f"Evaluation error: {str(exc)}")
    return {"error": str(exc)}

@app.exception_handler(EvaluationNotFoundError)
async def evaluation_not_found_handler(request: Request, exc: EvaluationNotFoundError):
    logger.error(f"Evaluation not found: {str(exc)}")
    return {"error": str(exc)}

@app.exception_handler(EvaluationValidationError)
async def evaluation_validation_handler(request: Request, exc: EvaluationValidationError):
    logger.error(f"Evaluation validation error: {str(exc)}")
    return {"error": str(exc)}

@app.exception_handler(MetricsError)
async def metrics_error_handler(request: Request, exc: MetricsError):
    logger.error(f"Metrics error: {str(exc)}")
    return {"error": str(exc)}

@app.exception_handler(MetricsNotFoundError)
async def metrics_not_found_handler(request: Request, exc: MetricsNotFoundError):
    logger.error(f"Metrics not found: {str(exc)}")
    return {"error": str(exc)}

@app.exception_handler(MetricsValidationError)
async def metrics_validation_handler(request: Request, exc: MetricsValidationError):
    logger.error(f"Metrics validation error: {str(exc)}")
    return {"error": str(exc)}

@app.exception_handler(DatabaseError)
async def database_error_handler(request: Request, exc: DatabaseError):
    logger.error(f"Database error: {str(exc)}")
    return {"error": str(exc)}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        workers=settings.api_workers,
        reload=settings.api_reload
    ) 