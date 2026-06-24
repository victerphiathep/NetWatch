from fastapi import APIRouter

from netwatch.api import data_access


router = APIRouter(tags=["readings"])


@router.get("/readings")
def get_raw_readings():
    return data_access.fetch_raw_readings()
