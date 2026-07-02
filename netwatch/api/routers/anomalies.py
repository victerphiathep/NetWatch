from fastapi import APIRouter

from netwatch.api import data_access
from netwatch.api.schemas import AnomalyReadingResponse


router = APIRouter(tags=["anomalies"])


@router.get("/anomalies", response_model=list[AnomalyReadingResponse])
def get_anomaly_readings():
    return data_access.fetch_anomaly_readings()
