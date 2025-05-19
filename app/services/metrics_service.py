from typing import List, Dict, Optional, Union
from datetime import datetime, timedelta
import uuid
from app.db.mongodb import MongoDB
from app.schemas.metrics import (
    MetricsResponse, MetricsFilter, MetricSeries, MetricValue,
    ChartConfig, MetricSummary, MetricComparison
)
from app.core.exceptions import (
    MetricsNotFoundError, DatasetNotFoundError, EvaluationNotFoundError,
    MetricsValidationError, DatabaseError
)
from app.core.retry import with_retry
import statistics
from collections import defaultdict
import logging
from pymongo.errors import ServerSelectionTimeoutError, OperationFailure

logger = logging.getLogger(__name__)

class MetricsService:
    @staticmethod
    @with_retry(
        max_retries=3,
        initial_delay=1.0,
        max_delay=10.0,
        exceptions=(ServerSelectionTimeoutError, OperationFailure)
    )
    async def get_usecase_metrics(
        usecase_id: str,
        filter_params: Optional[MetricsFilter] = None
    ) -> MetricsResponse:
        try:
            if not filter_params:
                filter_params = MetricsFilter()

            # Validate time range
            if filter_params.start_time and filter_params.end_time:
                if filter_params.start_time > filter_params.end_time:
                    raise MetricsValidationError("Start time must be before end time")

            # Build query
            query = {"usecase_id": usecase_id}
            if filter_params.start_time:
                query["timestamp"] = {"$gte": filter_params.start_time}
            if filter_params.end_time:
                query["timestamp"] = query.get("timestamp", {})
                query["timestamp"]["$lte"] = filter_params.end_time

            # Get metrics
            metrics = await MongoDB.db.metrics.find(query).to_list(None)
            if not metrics:
                raise MetricsNotFoundError(f"No metrics found for usecase {usecase_id}")

            # Process metrics
            series = await MetricsService._aggregate_metrics(metrics, filter_params)
            summary = await MetricsService._generate_summary(series) if filter_params.include_summary else None
            comparison = await MetricsService._generate_comparison(series, filter_params) if filter_params.include_comparison else None

            # Create chart config
            chart_config = ChartConfig(
                type=filter_params.chart_type or "line",
                title=f"Metrics for Usecase {usecase_id}",
                x_axis_label="Time",
                y_axis_label="Value"
            )

            return MetricsResponse(
                usecase_id=usecase_id,
                series=series,
                chart_config=chart_config,
                summary=summary,
                comparison=comparison
            )
        except (MetricsNotFoundError, MetricsValidationError):
            raise
        except Exception as e:
            logger.error(f"Error getting usecase metrics: {str(e)}")
            raise DatabaseError(f"Failed to get usecase metrics: {str(e)}")

    @staticmethod
    @with_retry(
        max_retries=3,
        initial_delay=1.0,
        max_delay=10.0,
        exceptions=(ServerSelectionTimeoutError, OperationFailure)
    )
    async def get_dataset_metrics(
        usecase_id: str,
        dataset_id: str,
        filter_params: Optional[MetricsFilter] = None
    ) -> MetricsResponse:
        try:
            # Verify dataset exists
            dataset = await MongoDB.db.datasets.find_one({
                "id": dataset_id,
                "usecase_id": usecase_id
            })
            if not dataset:
                raise DatasetNotFoundError(dataset_id)

            if not filter_params:
                filter_params = MetricsFilter()

            # Validate time range
            if filter_params.start_time and filter_params.end_time:
                if filter_params.start_time > filter_params.end_time:
                    raise MetricsValidationError("Start time must be before end time")

            # Build query
            query = {
                "usecase_id": usecase_id,
                "dataset_id": dataset_id
            }
            if filter_params.start_time:
                query["timestamp"] = {"$gte": filter_params.start_time}
            if filter_params.end_time:
                query["timestamp"] = query.get("timestamp", {})
                query["timestamp"]["$lte"] = filter_params.end_time

            # Get metrics
            metrics = await MongoDB.db.metrics.find(query).to_list(None)
            if not metrics:
                raise MetricsNotFoundError(f"No metrics found for dataset {dataset_id}")

            # Process metrics
            series = await MetricsService._aggregate_metrics(metrics, filter_params)
            summary = await MetricsService._generate_summary(series) if filter_params.include_summary else None
            comparison = await MetricsService._generate_comparison(series, filter_params) if filter_params.include_comparison else None

            # Create chart config
            chart_config = ChartConfig(
                type=filter_params.chart_type or "line",
                title=f"Metrics for Dataset {dataset_id}",
                x_axis_label="Time",
                y_axis_label="Value"
            )

            return MetricsResponse(
                usecase_id=usecase_id,
                dataset_id=dataset_id,
                series=series,
                chart_config=chart_config,
                summary=summary,
                comparison=comparison
            )
        except (DatasetNotFoundError, MetricsNotFoundError, MetricsValidationError):
            raise
        except Exception as e:
            logger.error(f"Error getting dataset metrics: {str(e)}")
            raise DatabaseError(f"Failed to get dataset metrics: {str(e)}")

    @staticmethod
    @with_retry(
        max_retries=3,
        initial_delay=1.0,
        max_delay=10.0,
        exceptions=(ServerSelectionTimeoutError, OperationFailure)
    )
    async def get_evaluation_metrics(
        usecase_id: str,
        evaluation_id: str,
        filter_params: Optional[MetricsFilter] = None
    ) -> MetricsResponse:
        try:
            # Verify evaluation exists
            evaluation = await MongoDB.db.evaluations.find_one({
                "id": evaluation_id,
                "usecase_id": usecase_id
            })
            if not evaluation:
                raise EvaluationNotFoundError(evaluation_id)

            if not filter_params:
                filter_params = MetricsFilter()

            # Validate time range
            if filter_params.start_time and filter_params.end_time:
                if filter_params.start_time > filter_params.end_time:
                    raise MetricsValidationError("Start time must be before end time")

            # Build query
            query = {
                "usecase_id": usecase_id,
                "evaluation_id": evaluation_id
            }
            if filter_params.start_time:
                query["timestamp"] = {"$gte": filter_params.start_time}
            if filter_params.end_time:
                query["timestamp"] = query.get("timestamp", {})
                query["timestamp"]["$lte"] = filter_params.end_time

            # Get metrics
            metrics = await MongoDB.db.metrics.find(query).to_list(None)
            if not metrics:
                raise MetricsNotFoundError(f"No metrics found for evaluation {evaluation_id}")

            # Process metrics
            series = await MetricsService._aggregate_metrics(metrics, filter_params)
            summary = await MetricsService._generate_summary(series) if filter_params.include_summary else None
            comparison = await MetricsService._generate_comparison(series, filter_params) if filter_params.include_comparison else None

            # Create chart config
            chart_config = ChartConfig(
                type=filter_params.chart_type or "line",
                title=f"Metrics for Evaluation {evaluation_id}",
                x_axis_label="Time",
                y_axis_label="Value"
            )

            return MetricsResponse(
                usecase_id=usecase_id,
                evaluation_id=evaluation_id,
                series=series,
                chart_config=chart_config,
                summary=summary,
                comparison=comparison
            )
        except (EvaluationNotFoundError, MetricsNotFoundError, MetricsValidationError):
            raise
        except Exception as e:
            logger.error(f"Error getting evaluation metrics: {str(e)}")
            raise DatabaseError(f"Failed to get evaluation metrics: {str(e)}")

    @staticmethod
    async def _aggregate_metrics(
        metrics: List[Dict],
        filter_params: MetricsFilter
    ) -> List[MetricSeries]:
        try:
            # Group metrics by name
            grouped_metrics = {}
            for metric in metrics:
                name = metric["name"]
                if name not in grouped_metrics:
                    grouped_metrics[name] = []

                # Apply value filters
                value = metric["value"]
                if filter_params.min_value is not None and value < filter_params.min_value:
                    continue
                if filter_params.max_value is not None and value > filter_params.max_value:
                    continue

                grouped_metrics[name].append(metric)

            # Create series
            series = []
            for name, values in grouped_metrics.items():
                # Sort values
                if filter_params.sort_by == "timestamp":
                    values.sort(key=lambda x: x["timestamp"])
                elif filter_params.sort_by == "value":
                    values.sort(key=lambda x: x["value"])

                if filter_params.sort_order == "desc":
                    values.reverse()

                # Apply limit
                if filter_params.limit:
                    values = values[:filter_params.limit]

                # Create metric values
                metric_values = [
                    MetricValue(
                        timestamp=value["timestamp"],
                        value=value["value"],
                        confidence_interval=value.get("confidence_interval")
                    )
                    for value in values
                ]

                series.append(MetricSeries(
                    name=name,
                    values=metric_values
                ))

            return series
        except Exception as e:
            logger.error(f"Error aggregating metrics: {str(e)}")
            raise DatabaseError(f"Failed to aggregate metrics: {str(e)}")

    @staticmethod
    async def _generate_summary(series: List[MetricSeries]) -> Dict[str, MetricSummary]:
        try:
            summaries = {}
            for s in series:
                values = [v.value for v in s.values]
                if not values:
                    continue

                summaries[s.name] = MetricSummary(
                    mean=statistics.mean(values),
                    median=statistics.median(values),
                    min=min(values),
                    max=max(values),
                    std_dev=statistics.stdev(values) if len(values) > 1 else 0,
                    count=len(values)
                )
            return summaries
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            raise DatabaseError(f"Failed to generate summary: {str(e)}")

    @staticmethod
    async def _generate_comparison(
        series: List[MetricSeries],
        filter_params: MetricsFilter
    ) -> Optional[MetricComparison]:
        try:
            if not filter_params.comparison_period and not filter_params.baseline_id:
                return None

            comparison = MetricComparison(
                period_change={},
                baseline_comparison={}
            )

            # Calculate period-over-period changes
            if filter_params.comparison_period:
                for s in series:
                    if len(s.values) < 2:
                        continue

                    current = s.values[-1].value
                    previous = s.values[0].value
                    change = ((current - previous) / previous) * 100 if previous != 0 else 0

                    comparison.period_change[s.name] = {
                        "current": current,
                        "previous": previous,
                        "change_percent": change
                    }

            # Compare with baseline
            if filter_params.baseline_id:
                baseline_metrics = await MongoDB.db.metrics.find({
                    "evaluation_id": filter_params.baseline_id
                }).to_list(None)

                if baseline_metrics:
                    baseline_series = await MetricsService._aggregate_metrics(
                        baseline_metrics,
                        MetricsFilter()
                    )

                    for s in series:
                        if not s.values:
                            continue

                        current = s.values[-1].value
                        baseline = next(
                            (bs for bs in baseline_series if bs.name == s.name),
                            None
                        )

                        if baseline and baseline.values:
                            baseline_value = baseline.values[-1].value
                            change = ((current - baseline_value) / baseline_value) * 100 if baseline_value != 0 else 0

                            comparison.baseline_comparison[s.name] = {
                                "current": current,
                                "baseline": baseline_value,
                                "change_percent": change
                            }

            return comparison
        except Exception as e:
            logger.error(f"Error generating comparison: {str(e)}")
            raise DatabaseError(f"Failed to generate comparison: {str(e)}") 