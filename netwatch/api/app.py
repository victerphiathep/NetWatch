from fastapi import FastAPI

from netwatch.api.routers import (
    anomalies,
    forecasts,
    health,
    nodes,
    readings,
    regions,
)


api_app = FastAPI(
    title="NetWatch API",
    description="Backend API for the NetWatch capacity monitoring project.",
    version="0.1.0",
)

api_app.include_router(health.router)
api_app.include_router(nodes.router)
api_app.include_router(readings.router)
api_app.include_router(anomalies.router)
api_app.include_router(forecasts.router)
api_app.include_router(regions.router)
