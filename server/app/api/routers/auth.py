from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Header, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import httpx
import jwt

from app.core.response import api_error, api_ok
from app.core.settings import settings
from app.core.database import get_db
from app.core.status import UserStatus
from app.services.user_service import UserService
from app.schemas.common import TokenRefreshRequest, WxLoginRequest

router = APIRouter(prefix="/api/auth", tags=["Auth"])


def _issue_token(payload: dict, expires_seconds: int) -> str:
    """签发 JWT token"""
    expire_at = datetime.now(timezone.utc) + timedelta(seconds=expires_seconds)
    token_payload = {**payload, "exp": expire_at}
    return jwt.encode(token_payload, settings.JWT_SECRET, algorithm="HS256")


def _wechat_code_to_session(code: str) -> dict:
    """调用微信接口，用 code 换取 openid"""
    response = httpx.get(
        "https://api.weixin.qq.com/sns/jscode2session",
        params={
            "appid": settings.WECHAT_APP_ID,
            "secret": settings.WECHAT_APP_SECRET,
            "js_code": code,
            "grant_type": "authorization_code",
        },
        timeout=8.0,
    )
    response.raise_for_status()
    return response.json()


def _json_error(status_code: int, code: int, message: str, data=None) -> JSONResponse:
    """统一错误响应"""
    return JSONResponse(
        status_code=status_code,
        content=api_error(message=message, code=code, data=data),
    )


def _get_current_user_from_token(
    authorization: Optional[str] = None,
    db: Session = None
) -> tuple[Optional[dict], Optional[JSONResponse]]:
    """
    从 Authorization header 解析当前用户
    返回: (用户信息, 错误响应)
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None, _json_error(401, 10030, "missing bearer token")

    token = authorization.split(" ", 1)[1]
    try:
        token_data = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None, _json_error(401, 10031, "access token invalid")

    if token_data.get("typ") != "access":
        return None, _json_error(401, 10032, "token type mismatch")

    user_service = UserService(db)
    user_info = user_service.get_simple_user_info(token_data.get("uid", 0))

    if not user_info:
        return None, _json_error(404, 10033, "user not found")

    return user_info, None


@router.post("/wx-login")
def wx_login(payload: WxLoginRequest, db: Session = Depends(get_db)):
    """微信授权登录"""
    if not settings.WECHAT_APP_ID or not settings.WECHAT_APP_SECRET:
        return _json_error(
            status_code=500,
            code=10010,
            message="server wechat config missing",
        )

    try:
        wx_result = _wechat_code_to_session(payload.code)
    except httpx.HTTPError:
        return _json_error(
            status_code=502,
            code=10011,
            message="wechat service unavailable",
        )

    if wx_result.get("errcode"):
        return _json_error(
            status_code=401,
            code=10012,
            message="wechat login failed",
            data={"wxErrCode": wx_result.get("errcode"), "wxErrMsg": wx_result.get("errmsg")},
        )

    openid = wx_result.get("openid", "")
    if not openid:
        return _json_error(
            status_code=401,
            code=10013,
            message="wechat openid missing",
        )

    # 判断是否应该设置为管理员（新增代码）
    is_admin = False
    if payload.admin_secret and payload.admin_secret in settings.ADMIN_CREATION_SECRETS:
        is_admin = True

    # 使用 service 层创建或获取用户（修改：传入 is_admin）
    user_service = UserService(db)
    user = user_service.create_or_get_user(openid, is_admin=is_admin)

    # 构建用户资料（修改：添加 is_admin）
    profile = {
        "id": user.id,
        "nickname": user.nickname,
        "avatar": user.avatar,
        "score": user.score,
        "status": user.status if user.status else UserStatus.ACTIVE.value,
        "is_admin": user.is_admin,  # 新增
    }

    # 签发 token（修改：添加 is_admin）
    access_token = _issue_token(
        {
            "sub": openid,
            "uid": user.id,
            "nickname": user.nickname,
            "is_admin": user.is_admin,  # 新增
            "typ": "access",
        },
        settings.JWT_EXPIRES_SECONDS,
    )
    refresh_token = _issue_token(
        {
            "sub": openid,
            "uid": user.id,
            "nickname": user.nickname,
            "is_admin": user.is_admin,  # 新增
            "typ": "refresh",
        },
        settings.JWT_REFRESH_EXPIRES_SECONDS,
    )

    return api_ok(
        {
            "accessToken": access_token,
            "refreshToken": refresh_token,
            "expiresIn": settings.JWT_EXPIRES_SECONDS,
            "user": profile,
        }
    )


@router.post("/refresh")
def refresh_token(payload: TokenRefreshRequest):
    """刷新 access token"""
    try:
        token_data = jwt.decode(payload.refreshToken, settings.JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        return _json_error(
            status_code=401,
            code=10020,
            message="refresh token invalid",
        )

    if token_data.get("typ") != "refresh":
        return _json_error(
            status_code=401,
            code=10021,
            message="token type mismatch",
        )

    # 修改：保留 is_admin 字段
    new_access_token = _issue_token(
        {
            "sub": token_data.get("sub"),
            "uid": token_data.get("uid"),
            "nickname": token_data.get("nickname", ""),
            "is_admin": token_data.get("is_admin", False),  # 新增
            "typ": "access",
        },
        settings.JWT_EXPIRES_SECONDS,
    )

    return api_ok(
        {
            "accessToken": new_access_token,
            "refreshToken": payload.refreshToken,
            "expiresIn": settings.JWT_EXPIRES_SECONDS,
        }
    )


@router.post("/logout")
def logout() -> dict:
    """登出（客户端删除 token 即可，服务端无需操作）"""
    return api_ok()


@router.get("/me")
def get_current_user(
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
):
    """获取当前登录用户信息（auth 模块版本）"""
    user_info, error_response = _get_current_user_from_token(authorization, db)
    if error_response:
        return error_response

    user_service = UserService(db)
    profile = user_service.get_user_profile(user_info["id"])

    if not profile:
        return _json_error(404, 10033, "user not found")

    return api_ok(profile)