from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Optional, Literal
from datetime import datetime
from app.schemas.metrics import MetricsResponse, MetricsFilter
from app.services.metrics_service import MetricsService
from app.core.exceptions import (
    MetricsValidationError, MetricsNotFoundError,
    DatasetNotFoundError, EvaluationNotFoundError,
    DatabaseError
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

async def validate_time_range(start_time: Optional[datetime], end_time: Optional[datetime]):
    if start_time and end_time and start_time > end_time:
        raise MetricsValidationError("start_time must be before end_time")
    return start_time, end_time

@router.get("/usecases/{usecase_id}/metrics", response_model=MetricsResponse)
async def get_usecase_metrics(
    usecase_id: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    metric_names: Optional[List[str]] = Query(None),
    aggregation_type: Optional[str] = None,
    group_by: Optional[List[str]] = Query(None),
    chart_type: Optional[Literal["line", "bar", "scatter", "pie", "heatmap", "radar", "gauge"]] = None,
    include_summary: bool = False,
    include_comparison: bool = False,
    comparison_period: Optional[str] = None,
    baseline_id: Optional[str] = None,
    categories: Optional[List[str]] = Query(None),
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[Literal["asc", "desc"]] = None,
    limit: Optional[int] = None
):
    try:
        # Validate time range
        start_time, end_time = await validate_time_range(start_time, end_time)

        # Validate comparison parameters
        if include_comparison and not (comparison_period or baseline_id):
            raise MetricsValidationError(
                "Either comparison_period or baseline_id must be provided when include_comparison is True"
            )

        # Validate value range
        if min_value is not None and max_value is not None and min_value > max_value:
            raise MetricsValidationError("min_value must be less than or equal to max_value")

        filter_params = MetricsFilter(
            start_time=start_time,
            end_time=end_time,
            metric_names=metric_names,
            aggregation_type=aggregation_type,
            group_by=group_by,
            chart_type=chart_type,
            include_summary=include_summary,
            include_comparison=include_comparison,
            comparison_period=comparison_period,
            baseline_id=baseline_id,
            categories=categories,
            min_value=min_value,
            max_value=max_value,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit
        )
        return await MetricsService.get_usecase_metrics(usecase_id, filter_params)
    except MetricsValidationError as e:
        logger.error(f"Validation error in get_usecase_metrics: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except MetricsNotFoundError as e:
        logger.error(f"Metrics not found in get_usecase_metrics: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error in get_usecase_metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in get_usecase_metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/usecases/{usecase_id}/datasets/{dataset_id}/metrics", response_model=MetricsResponse)
async def get_dataset_metrics(
    usecase_id: str,
    dataset_id: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    metric_names: Optional[List[str]] = Query(None),
    aggregation_type: Optional[str] = None,
    group_by: Optional[List[str]] = Query(None),
    chart_type: Optional[Literal["line", "bar", "scatter", "pie", "heatmap", "radar", "gauge"]] = None,
    include_summary: bool = False,
    include_comparison: bool = False,
    comparison_period: Optional[str] = None,
    baseline_id: Optional[str] = None,
    categories: Optional[List[str]] = Query(None),
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[Literal["asc", "desc"]] = None,
    limit: Optional[int] = None
):
    try:
        # Validate time range
        start_time, end_time = await validate_time_range(start_time, end_time)

        # Validate comparison parameters
        if include_comparison and not (comparison_period or baseline_id):
            raise MetricsValidationError(
                "Either comparison_period or baseline_id must be provided when include_comparison is True"
            )

        # Validate value range
        if min_value is not None and max_value is not None and min_value > max_value:
            raise MetricsValidationError("min_value must be less than or equal to max_value")

        filter_params = MetricsFilter(
            start_time=start_time,
            end_time=end_time,
            metric_names=metric_names,
            aggregation_type=aggregation_type,
            group_by=group_by,
            chart_type=chart_type,
            include_summary=include_summary,
            include_comparison=include_comparison,
            comparison_period=comparison_period,
            baseline_id=baseline_id,
            categories=categories,
            min_value=min_value,
            max_value=max_value,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit
        )
        return await MetricsService.get_dataset_metrics(usecase_id, dataset_id, filter_params)
    except MetricsValidationError as e:
        logger.error(f"Validation error in get_dataset_metrics: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except (MetricsNotFoundError, DatasetNotFoundError) as e:
        logger.error(f"Resource not found in get_dataset_metrics: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error in get_dataset_metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in get_dataset_metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/usecases/{usecase_id}/evaluations/{evaluation_id}/metrics", response_model=MetricsResponse)
async def get_evaluation_metrics(
    usecase_id: str,
    evaluation_id: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    metric_names: Optional[List[str]] = Query(None),
    aggregation_type: Optional[str] = None,
    group_by: Optional[List[str]] = Query(None),
    chart_type: Optional[Literal["line", "bar", "scatter", "pie", "heatmap", "radar", "gauge"]] = None,
    include_summary: bool = False,
    include_comparison: bool = False,
    comparison_period: Optional[str] = None,
    baseline_id: Optional[str] = None,
    categories: Optional[List[str]] = Query(None),
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[Literal["asc", "desc"]] = None,
    limit: Optional[int] = None
):
    try:
        # Validate time range
        start_time, end_time = await validate_time_range(start_time, end_time)

        # Validate comparison parameters
        if include_comparison and not (comparison_period or baseline_id):
            raise MetricsValidationError(
                "Either comparison_period or baseline_id must be provided when include_comparison is True"
            )

        # Validate value range
        if min_value is not None and max_value is not None and min_value > max_value:
            raise MetricsValidationError("min_value must be less than or equal to max_value")

        filter_params = MetricsFilter(
            start_time=start_time,
            end_time=end_time,
            metric_names=metric_names,
            aggregation_type=aggregation_type,
            group_by=group_by,
            chart_type=chart_type,
            include_summary=include_summary,
            include_comparison=include_comparison,
            comparison_period=comparison_period,
            baseline_id=baseline_id,
            categories=categories,
            min_value=min_value,
            max_value=max_value,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit
        )
        return await MetricsService.get_evaluation_metrics(usecase_id, evaluation_id, filter_params)
    except MetricsValidationError as e:
        logger.error(f"Validation error in get_evaluation_metrics: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except (MetricsNotFoundError, EvaluationNotFoundError) as e:
        logger.error(f"Resource not found in get_evaluation_metrics: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error in get_evaluation_metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in get_evaluation_metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error") 