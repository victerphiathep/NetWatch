from fastapi import APIRouter, HTTPException

from netwatch.api import data_access


router = APIRouter(prefix="/forecasts", tags=["forecasts"])


@router.get("")
def get_node_forecasts():
    return data_access.fetch_node_forecasts()


@router.get("/{node_id}")
def get_node_forecast(node_id: str):
    node_forecast = data_access.fetch_node_forecast(node_id)

    if node_forecast is None:
        raise HTTPException(status_code=404, detail="Node forecast not found")

    return node_forecast
