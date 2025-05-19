from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Optional, Union, Literal
import uuid

class MetricValue(BaseModel):
    timestamp: datetime
    value: float
    metadata: Optional[Dict] = None
    confidence_interval: Optional[Dict[str, float]] = None  # For error bars
    category: Optional[str] = None  # For grouped/stacked charts
    label: Optional[str] = None  # Custom label for the data point

class MetricSeries(BaseModel):
    name: str
    values: List[MetricValue]
    aggregation_type: str  # e.g., "sum", "avg", "count", "min", "max"
    unit: Optional[str] = None
    chart_type: Optional[Literal["line", "bar", "scatter", "pie", "heatmap"]] = "line"
    color: Optional[str] = None
    y_axis: Optional[str] = None  # For dual-axis charts
    stack_group: Optional[str] = None  # For stacked charts
    show_in_legend: bool = True
    metadata: Optional[Dict] = None

class ChartConfig(BaseModel):
    type: Literal["line", "bar", "scatter", "pie", "heatmap", "radar", "gauge"] = "line"
    title: Optional[str] = None
    x_axis_label: Optional[str] = None
    y_axis_label: Optional[str] = None
    show_legend: bool = True
    stacked: bool = False
    dual_axis: bool = False
    theme: Optional[str] = None
    height: Optional[int] = None
    width: Optional[int] = None
    annotations: Optional[List[Dict]] = None
    thresholds: Optional[List[Dict[str, Union[float, str]]]] = None

class MetricSummary(BaseModel):
    mean: float
    median: float
    min: float
    max: float
    std_dev: float
    count: int
    percentiles: Optional[Dict[str, float]] = None  # e.g., {"25": 1.5, "75": 2.5, "90": 3.0}
    confidence_interval: Optional[Dict[str, float]] = None  # e.g., {"lower": 1.0, "upper": 3.0}

class MetricComparison(BaseModel):
    period_change: Dict[str, Dict[str, Union[float, str]]]  # e.g., {"metric_name": {"current": 1.5, "previous": 1.0, "change_percent": 50.0}}
    baseline_comparison: Dict[str, Dict[str, Union[float, str]]]  # e.g., {"metric_name": {"current": 1.5, "baseline": 1.0, "change_percent": 50.0}}

class MetricsResponse(BaseModel):
    id: str = str(uuid.uuid4())
    usecase_id: str
    dataset_id: Optional[str] = None
    evaluation_id: Optional[str] = None
    metrics: List[MetricSeries]
    time_range: Dict[str, datetime]  # start and end timestamps
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    chart_config: Optional[ChartConfig] = None
    summary: Optional[Dict[str, MetricSummary]] = None
    comparison: Optional[MetricComparison] = None

    class Config:
        from_attributes = True

class MetricsFilter(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    metric_names: Optional[List[str]] = None
    aggregation_type: Optional[str] = None
    group_by: Optional[List[str]] = None  # e.g., ["hour", "day", "week"]
    chart_type: Optional[Literal["line", "bar", "scatter", "pie", "heatmap", "radar", "gauge"]] = None
    include_summary: bool = False
    include_comparison: bool = False
    comparison_period: Optional[str] = None  # e.g., "previous_week", "previous_month"
    baseline_id: Optional[str] = None  # For comparing with a baseline evaluation
    categories: Optional[List[str]] = None  # For filtering by categories
    min_value: Optional[float] = None  # For filtering by value range
    max_value: Optional[float] = None
    sort_by: Optional[str] = None  # For sorting the results
    sort_order: Optional[Literal["asc", "desc"]] = None
    limit: Optional[int] = None  # For limiting the number of results 