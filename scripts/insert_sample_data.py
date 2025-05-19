import os
import sys
from pathlib import Path
import asyncio
import logging
from datetime import datetime, timedelta, UTC
import random
import uuid

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from app.db.mongodb import MongoDB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def insert_sample_data():
    """Insert sample data into MongoDB collections."""
    try:
        # Connect to MongoDB
        await MongoDB.connect_to_database()
        db = MongoDB.db

        # Clear existing data
        logger.info("Clearing existing data...")
        await db.datasets.delete_many({})
        await db.evaluations.delete_many({})
        await db.metrics.delete_many({})
        logger.info("Existing data cleared")

        # Sample usecase IDs
        usecase_ids = ["usecase_001", "usecase_002", "usecase_003"]
        
        # Insert sample datasets
        datasets = []
        for usecase_id in usecase_ids:
            for i in range(2):  # 2 datasets per usecase
                dataset = {
                    "id": str(uuid.uuid4()),
                    "usecase_id": usecase_id,
                    "name": f"Dataset {i+1} for {usecase_id}",
                    "alias": f"dataset_{usecase_id}_{i+1}_{str(uuid.uuid4())[:8]}",  # Added unique suffix
                    "description": f"Sample dataset {i+1} for {usecase_id}",
                    "created_at": datetime.now(UTC) - timedelta(days=random.randint(1, 30)),
                    "updated_at": datetime.now(UTC)
                }
                datasets.append(dataset)
        
        if datasets:
            await db.datasets.insert_many(datasets)
            logger.info(f"Inserted {len(datasets)} sample datasets")

        # Insert sample evaluations
        evaluations = []
        for dataset in datasets:
            for i in range(3):  # 3 evaluations per dataset
                status = random.choice(["pending", "running", "completed", "failed"])
                now = datetime.now(UTC)
                created_at = now - timedelta(days=random.randint(1, 30))
                
                evaluation = {
                    "id": str(uuid.uuid4()),
                    "usecase_id": dataset["usecase_id"],
                    "dataset_id": dataset["id"],
                    "model_version": f"v1.{random.randint(0, 5)}.{random.randint(0, 9)}",
                    "parameters": {
                        "batch_size": random.choice([32, 64, 128]),
                        "learning_rate": random.uniform(0.0001, 0.01),
                        "epochs": random.randint(10, 100)
                    },
                    "status": status,
                    "result": {
                        "accuracy": random.uniform(0.7, 0.99),
                        "precision": random.uniform(0.7, 0.99),
                        "recall": random.uniform(0.7, 0.99),
                        "f1_score": random.uniform(0.7, 0.99)
                    } if status == "completed" else {},
                    "error": "Sample error message" if status == "failed" else "",
                    "created_at": created_at,
                    "updated_at": now,
                    "completed_at": now if status == "completed" else created_at,
                    "failed_at": now if status == "failed" else created_at
                }
                evaluations.append(evaluation)
        
        if evaluations:
            await db.evaluations.insert_many(evaluations)
            logger.info(f"Inserted {len(evaluations)} sample evaluations")

        # Insert sample metrics
        metrics = []
        metric_names = ["accuracy", "precision", "recall", "f1_score", "latency", "throughput"]
        
        for evaluation in evaluations:
            if evaluation["status"] == "completed":
                for metric_name in metric_names:
                    # Generate 10 data points for each metric
                    for i in range(10):
                        timestamp = evaluation["completed_at"] - timedelta(minutes=i*5)
                        metric = {
                            "usecase_id": evaluation["usecase_id"],
                            "dataset_id": evaluation["dataset_id"],
                            "evaluation_id": evaluation["id"],
                            "name": metric_name,
                            "value": random.uniform(0.7, 0.99) if metric_name != "latency" else random.uniform(10, 100),
                            "timestamp": timestamp,
                            "confidence_interval": {
                                "lower": random.uniform(0.65, 0.85),
                                "upper": random.uniform(0.85, 0.99)
                            } if metric_name != "latency" else None
                        }
                        metrics.append(metric)
        
        if metrics:
            await db.metrics.insert_many(metrics)
            logger.info(f"Inserted {len(metrics)} sample metrics")

        logger.info("Sample data insertion completed successfully")

    except Exception as e:
        logger.error(f"Error inserting sample data: {str(e)}")
        raise
    finally:
        await MongoDB.close_database_connection()

if __name__ == "__main__":
    asyncio.run(insert_sample_data()) 