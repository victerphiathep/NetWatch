from fastapi import APIRouter

from netwatch.api import data_access
from netwatch.api.schemas import RawNodeReadingResponse


router = APIRouter(tags=["readings"])


@router.get("/readings", response_model=list[RawNodeReadingResponse])
def get_raw_readings():
    return data_access.fetch_raw_readings()
