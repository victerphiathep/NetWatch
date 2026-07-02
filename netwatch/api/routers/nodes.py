from fastapi import APIRouter, HTTPException, Query

from netwatch.api import data_access
from netwatch.api.schemas import (
    AnomalyReadingResponse,
    NodeForecastResponse,
    NodeSummaryResponse,
    RawNodeReadingResponse,
)


router = APIRouter(prefix="/nodes", tags=["nodes"])


@router.get("", response_model=list[NodeSummaryResponse])
def get_node_summaries():
    return data_access.fetch_node_summaries()


@router.get("/{node_id}", response_model=NodeSummaryResponse)
def get_node_summary(node_id: str):
    node_summary = data_access.fetch_node_summary(node_id)

    if node_summary is None:
        raise HTTPException(status_code=404, detail="Node not found")

    return node_summary


@router.get("/{node_id}/readings", response_model=list[RawNodeReadingResponse])
def get_node_readings(
    node_id: str,
    limit: int = Query(default=168, ge=1, le=1000),
):
    node_summary = data_access.fetch_node_summary(node_id)

    if node_summary is None:
        raise HTTPException(status_code=404, detail="Node not found")

    return data_access.fetch_node_readings(node_id, limit)


@router.get("/{node_id}/anomalies", response_model=list[AnomalyReadingResponse])
def get_node_anomalies(node_id: str):
    node_summary = data_access.fetch_node_summary(node_id)

    if node_summary is None:
        raise HTTPException(status_code=404, detail="Node not found")

    return data_access.fetch_node_anomalies(node_id)


@router.get("/{node_id}/forecast", response_model=NodeForecastResponse)
def get_node_forecast(node_id: str):
    node_summary = data_access.fetch_node_summary(node_id)

    if node_summary is None:
        raise HTTPException(status_code=404, detail="Node not found")

    node_forecast = data_access.fetch_node_forecast(node_id)

    if node_forecast is None:
        raise HTTPException(status_code=404, detail="Node forecast not found")

    return node_forecast
