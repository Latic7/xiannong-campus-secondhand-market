from fastapi import FastAPI

from app.api.routers import ROUTERS
from app.core.response import api_ok

app = FastAPI(
    title="Campus Second-hand Market API",
    version="0.1.0-draft",
    description="FastAPI skeleton generated from OpenAPI draft.",
)


@app.get("/health")
def health_check() -> dict:
    return api_ok({"status": "up"})


for router in ROUTERS:
    app.include_router(router)
