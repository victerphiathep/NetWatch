from fastapi import FastAPI, HTTPException, Query

from netwatch.api import data_access


api_app = FastAPI(
    title="NetWatch API",
    description="Backend API for the NetWatch capacity monitoring project.",
    version="0.1.0",
)


@api_app.get("/health")
def get_health_status():
    return {"status": "ok", "service": "netwatch-api"}


@api_app.get("/nodes")
def get_node_summaries():
    return data_access.fetch_node_summaries()


@api_app.get("/nodes/{node_id}")
def get_node_summary(node_id: str):
    node_summary = data_access.fetch_node_summary(node_id)

    if node_summary is None:
        raise HTTPException(status_code=404, detail="Node not found")

    return node_summary


@api_app.get("/nodes/{node_id}/readings")
def get_node_readings(
    node_id: str,
    limit: int = Query(default=168, ge=1, le=1000),
):
    node_summary = data_access.fetch_node_summary(node_id)

    if node_summary is None:
        raise HTTPException(status_code=404, detail="Node not found")

    return data_access.fetch_node_readings(node_id, limit)


@api_app.get("/nodes/{node_id}/anomalies")
def get_node_anomalies(node_id: str):
    node_summary = data_access.fetch_node_summary(node_id)

    if node_summary is None:
        raise HTTPException(status_code=404, detail="Node not found")

    return data_access.fetch_node_anomalies(node_id)


@api_app.get("/regions")
def get_regions():
    region_rows = data_access.fetch_regions()
    return [region_row["region"] for region_row in region_rows]


@api_app.get("/regions/risk-summary")
def get_region_risk_summary():
    return data_access.fetch_region_risk_summary()
