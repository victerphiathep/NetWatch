from fastapi import APIRouter

from netwatch.api.schemas import HealthStatusResponse


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthStatusResponse)
def get_health_status():
    return {"status": "ok", "service": "netwatch-api"}
