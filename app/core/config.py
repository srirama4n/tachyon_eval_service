from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # MongoDB Configuration
    mongodb_url: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    mongodb_db_name: str = os.getenv("MONGODB_DB_NAME", "tachyon_eval")

    # API Configuration
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    api_workers: int = int(os.getenv("API_WORKERS", "4"))
    api_reload: bool = os.getenv("API_RELOAD", "true").lower() == "true"

    # Logging Configuration
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_format: str = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Security
    api_key_header: str = os.getenv("API_KEY_HEADER", "X-API-Key")
    api_key: str = os.getenv("API_KEY", "")

    # Metrics Configuration
    metrics_retention_days: int = int(os.getenv("METRICS_RETENTION_DAYS", "30"))
    metrics_aggregation_interval: str = os.getenv("METRICS_AGGREGATION_INTERVAL", "1h")

    # Evaluation Configuration
    max_concurrent_evaluations: int = int(os.getenv("MAX_CONCURRENT_EVALUATIONS", "10"))
    evaluation_timeout_seconds: int = int(os.getenv("EVALUATION_TIMEOUT_SECONDS", "3600"))

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields

@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    """
    return Settings()

# Create a global settings instance
settings = get_settings() 