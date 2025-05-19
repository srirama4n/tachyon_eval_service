import asyncio
import logging
import uuid
from datetime import datetime, UTC
from app.db.mongodb import MongoDB
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def insert_sample_data():
    try:
        # Connect to MongoDB
        await MongoDB.connect()
        logger.info("Connected to MongoDB")

        # Sample usecase ID
        usecase_id = "sample-usecase-1"

        # Insert sample dataset
        dataset = {
            "id": str(uuid.uuid4()),
            "usecase_id": usecase_id,
            "name": "Sample Dataset",
            "description": "A sample dataset for testing",
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC)
        }
        await MongoDB.db.datasets.insert_one(dataset)
        logger.info(f"Inserted sample dataset: {dataset['id']}")

        # Insert sample goldens
        goldens = [
            {
                "id": str(uuid.uuid4()),
                "dataset_id": dataset["id"],
                "usecase_id": usecase_id,
                "input": "What is the capital of France?",
                "actualOutput": "The capital of France is Paris.",
                "expectedOutput": "Paris",
                "context": "Geography question about European capitals",
                "retrievalContext": "France is a country in Western Europe. Its capital is Paris.",
                "created_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC)
            },
            {
                "id": str(uuid.uuid4()),
                "dataset_id": dataset["id"],
                "usecase_id": usecase_id,
                "input": "Who wrote Romeo and Juliet?",
                "actualOutput": "Romeo and Juliet was written by William Shakespeare.",
                "expectedOutput": "William Shakespeare",
                "context": "Literature question about famous plays",
                "retrievalContext": "Romeo and Juliet is a tragedy written by William Shakespeare.",
                "created_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC)
            }
        ]
        await MongoDB.db.goldens.insert_many(goldens)
        logger.info(f"Inserted {len(goldens)} sample goldens")

        # Insert sample evaluation
        evaluation = {
            "id": str(uuid.uuid4()),
            "dataset_id": dataset["id"],
            "usecase_id": usecase_id,
            "test_name": "Sample Evaluation",
            "model_id": "gpt-3.5-turbo",
            "temperature": "0.7",
            "parameters": [
                {"name": "max_tokens", "value": "100"},
                {"name": "top_p", "value": "0.9"}
            ],
            "status": "completed",
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
            "completed_at": datetime.now(UTC)
        }
        await MongoDB.db.evaluations.insert_one(evaluation)
        logger.info(f"Inserted sample evaluation: {evaluation['id']}")

        # Insert sample metrics
        metrics = [
            {
                "usecase_id": usecase_id,
                "dataset_id": dataset["id"],
                "evaluation_id": evaluation["id"],
                "metric_name": "accuracy",
                "metric_value": 0.85,
                "timestamp": datetime.now(UTC)
            },
            {
                "usecase_id": usecase_id,
                "dataset_id": dataset["id"],
                "evaluation_id": evaluation["id"],
                "metric_name": "response_time",
                "metric_value": 1.2,
                "timestamp": datetime.now(UTC)
            }
        ]
        await MongoDB.db.metrics.insert_many(metrics)
        logger.info(f"Inserted {len(metrics)} sample metrics")

        logger.info("Sample data insertion completed successfully")
    except Exception as e:
        logger.error(f"Error inserting sample data: {str(e)}")
        raise
    finally:
        await MongoDB.close()

if __name__ == "__main__":
    asyncio.run(insert_sample_data()) 