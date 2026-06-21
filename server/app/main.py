import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError  # 新增导入

from app.api.routers import ROUTERS
from app.core.exceptions import BusinessError
from app.core.response import api_error, api_ok
from app.core.settings import settings
from app.db.init_db import init_db

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Campus Second-hand Market API",
    version="0.1.0-draft",
    description="FastAPI skeleton generated from OpenAPI draft.",
)


@app.on_event("startup")
def on_startup() -> None:
    """应用启动时初始化数据库，失败时只打日志不阻止启动"""
    try:
        init_db()
        logger.info("Database tables initialized successfully")
    except Exception as exc:
        logger.warning("Database initialization skipped: %s", exc)

# 挂载 static 目录为静态文件，供上传的图片访问（仅本地存储模式下需要）
# COS 模式下图片由腾讯云对象存储直接提供，无需挂载本地目录
if not settings.cos_enabled:
    static_dir = Path(settings.static_dir)
    static_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.exception_handler(BusinessError)
def handle_business_error(_, exc: BusinessError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=api_error(message=exc.message, code=exc.code, data=exc.data),
    )


# 新增：处理 Pydantic 请求体验证错误（422）
@app.exception_handler(RequestValidationError)
def handle_validation_error(_, exc: RequestValidationError) -> JSONResponse:
    """统一处理 422 验证错误，返回 ApiResponse 格式"""
    errors = []
    for error in exc.errors():
        # 提取字段路径
        loc = error.get("loc", [])
        # 跳过 "body" 前缀，只保留字段名
        field = ".".join(str(item) for item in loc if item not in ("body", "query", "path"))
        errors.append({
            "field": field,
            "message": error.get("msg", "validation error"),
        })
    
    return JSONResponse(
        status_code=422,
        content=api_error(
            code=10001,
            message="validation error",
            data={"errors": errors},
        ),
    )


@app.get("/health")
def health_check() -> dict:
    return api_ok({"status": "up"})


for router in ROUTERS:
    app.include_router(router)