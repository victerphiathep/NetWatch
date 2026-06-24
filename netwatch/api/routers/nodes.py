from fastapi import APIRouter, HTTPException, Query

from netwatch.api import data_access


router = APIRouter(prefix="/nodes", tags=["nodes"])


@router.get("")
def get_node_summaries():
    return data_access.fetch_node_summaries()


@router.get("/{node_id}")
def get_node_summary(node_id: str):
    node_summary = data_access.fetch_node_summary(node_id)

    if node_summary is None:
        raise HTTPException(status_code=404, detail="Node not found")

    return node_summary


@router.get("/{node_id}/readings")
def get_node_readings(
    node_id: str,
    limit: int = Query(default=168, ge=1, le=1000),
):
    node_summary = data_access.fetch_node_summary(node_id)

    if node_summary is None:
        raise HTTPException(status_code=404, detail="Node not found")

    return data_access.fetch_node_readings(node_id, limit)


@router.get("/{node_id}/anomalies")
def get_node_anomalies(node_id: str):
    node_summary = data_access.fetch_node_summary(node_id)

    if node_summary is None:
        raise HTTPException(status_code=404, detail="Node not found")

    return data_access.fetch_node_anomalies(node_id)
