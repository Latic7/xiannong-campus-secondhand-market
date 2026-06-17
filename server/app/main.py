from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routers import ROUTERS
from app.core.exceptions import BusinessError
from app.core.response import api_error, api_ok
from app.core.settings import settings
from app.db.init_db import init_db

app = FastAPI(
    title="Campus Second-hand Market API",
    version="0.1.0-draft",
    description="FastAPI skeleton generated from OpenAPI draft.",
)

init_db()

# 挂载 static 目录为静态文件，供上传的图片访问
static_dir = Path(settings.static_dir)
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.exception_handler(BusinessError)
def handle_business_error(_, exc: BusinessError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=api_error(message=exc.message, code=exc.code, data=exc.data),
    )


@app.get("/health")
def health_check() -> dict:
    return api_ok({"status": "up"})


for router in ROUTERS:
    app.include_router(router)
