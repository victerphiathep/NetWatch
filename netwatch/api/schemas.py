from datetime import date
from typing import Optional

from pydantic import BaseModel


class HealthStatusResponse(BaseModel):
    status: str
    service: str


class RawNodeReadingResponse(BaseModel):
    timestamp: str
    node_id: str
    region: str
    download_utilization_pct: float
    upload_utilization_pct: float
    capacity_mbps: int
    status: str


class AnomalyReadingResponse(BaseModel):
    timestamp: str
    node_id: str
    region: str
    download_utilization_pct: float
    node_avg_download_utilization: float
    node_std_download_utilization: float
    anomaly_threshold: float
    anomaly_score: float


class NodeSummaryResponse(BaseModel):
    node_id: str
    region: str
    avg_download_utilization: float
    max_download_utilization: float
    avg_upload_utilization: float
    max_upload_utilization: float
    total_reading_count: int
    critical_reading_count: int
    peak_hour_avg_download_utilization: float
    peak_hour_max_download_utilization: float
    peak_hour_total_reading_count: int
    peak_hour_critical_reading_count: int
    first_day_avg_download_utilization: float
    last_day_avg_download_utilization: float
    critical_reading_pct: float
    download_utilization_change: float
    risk_level: str


class NodeForecastResponse(BaseModel):
    node_id: str
    region: str
    first_reading_date: date
    last_reading_date: date
    first_day_avg_download_utilization: float
    last_day_avg_download_utilization: float
    daily_download_utilization_change: float
    projected_7_day_download_utilization: float
    projected_30_day_download_utilization: float
    days_until_critical: Optional[float]
    forecast_risk_level: str


class RegionRiskSummaryResponse(BaseModel):
    region: str
    risk_level: str
    node_count: int
