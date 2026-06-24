from fastapi import APIRouter

from netwatch.api import data_access


router = APIRouter(prefix="/regions", tags=["regions"])


@router.get("")
def get_regions():
    region_rows = data_access.fetch_regions()
    return [region_row["region"] for region_row in region_rows]


@router.get("/risk-summary")
def get_region_risk_summary():
    return data_access.fetch_region_risk_summary()
