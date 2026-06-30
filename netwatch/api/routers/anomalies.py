from fastapi import APIRouter

from netwatch.api import data_access


router = APIRouter(tags=["anomalies"])


@router.get("/anomalies")
def get_anomaly_readings():
    return data_access.fetch_anomaly_readings()
