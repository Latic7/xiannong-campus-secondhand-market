from datetime import datetime, timezone
from uuid import uuid4
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.settings import settings
from app.core.exceptions import BusinessError


def api_ok(data=None, message: str = "ok", code: int = 0) -> dict:
    return {
        "code": code,
        "message": message,
        "data": data,
        "requestId": str(uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def api_error(message: str, code: int, data=None) -> dict:
    return {
        "code": code,
        "message": message,
        "data": data,
        "requestId": str(uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def register_exception_handlers(app: FastAPI):
    """注册全局异常处理器"""
    
    @app.exception_handler(BusinessError)
    async def business_error_handler(request: Request, exc: BusinessError):
        return JSONResponse(
            status_code=exc.status_code,
            content=api_error(
                code=exc.code,
                message=exc.message,
                data=exc.data,
            ),
        )
    
    @app.exception_handler(Exception)
    async def general_error_handler(request: Request, exc: Exception):
        # 生产环境不暴露详细错误
        error_detail = str(exc) if getattr(settings, "DEBUG", False) else None
        return JSONResponse(
            status_code=500,
            content=api_error(
                code=10000,
                message="internal server error",
                data={"detail": error_detail} if error_detail else None,
            ),
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        """处理 Pydantic 请求体验证错误，统一为 ApiResponse 格式"""
        errors = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error.get("loc", []))
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