from datetime import datetime, timedelta, timezone
import hashlib
from fastapi import APIRouter, Header, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import httpx
import jwt

from app.core.response import api_error, api_ok
from app.core.settings import settings
from app.core.database import get_db
from app.core.status import UserStatus
from app.models.user import User
from app.schemas.common import TokenRefreshRequest, WxLoginRequest

router = APIRouter(prefix="/api/auth", tags=["Auth"])


def _issue_token(payload: dict, expires_seconds: int) -> str:
    expire_at = datetime.now(timezone.utc) + timedelta(seconds=expires_seconds)
    token_payload = {**payload, "exp": expire_at}
    return jwt.encode(token_payload, settings.JWT_SECRET, algorithm="HS256")


def _wechat_code_to_session(code: str) -> dict:
    """调用微信接口获取 openid"""
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
    return JSONResponse(
        status_code=status_code,
        content=api_error(message=message, code=code, data=data),
    )


@router.post("/wx-login")
def wx_login(
    payload: WxLoginRequest,
    db: Session = Depends(get_db)
):
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

    # 生成用户ID（8位十六进制哈希）
    user_id = int(hashlib.sha256(openid.encode("utf-8")).hexdigest()[:8], 16)
    
    # 查询或创建用户
    user = db.query(User).filter(User.openid == openid).first()
    
    if not user:
        user = User(
            id=user_id,
            openid=openid,
            nickname=f"WX_{openid[-6:]}",
            avatar="",
            score=100,
            status=UserStatus.ACTIVE,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # 构建用户资料返回
    profile = {
        "id": user.id,
        "nickname": user.nickname,
        "avatar": user.avatar,
        "score": user.score,
        "status": user.status.value,
    }

    # 签发 token
    access_token = _issue_token(
        {
            "sub": openid,
            "uid": user.id,
            "nickname": user.nickname,
            "typ": "access",
        },
        settings.JWT_EXPIRES_SECONDS,
    )
    refresh_token = _issue_token(
        {
            "sub": openid,
            "uid": user.id,
            "nickname": user.nickname,
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

    new_access_token = _issue_token(
        {
            "sub": token_data.get("sub"),
            "uid": token_data.get("uid"),
            "nickname": token_data.get("nickname", ""),
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
    """注销（客户端清除 token 即可）"""
    return api_ok()


@router.get("/me")
def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db)
):
    """获取当前登录用户信息（通过 token）"""
    if not authorization or not authorization.startswith("Bearer "):
        return _json_error(status_code=401, code=10030, message="missing bearer token")

    token = authorization.split(" ", 1)[1]
    try:
        token_data = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        return _json_error(status_code=401, code=10031, message="access token invalid")

    if token_data.get("typ") != "access":
        return _json_error(status_code=401, code=10032, message="token type mismatch")

    # 从数据库获取最新用户信息
    user = db.query(User).filter(User.id == token_data.get("uid")).first()
    if not user:
        return _json_error(status_code=404, code=10033, message="user not found")

    return api_ok(
        {
            "id": user.id,
            "nickname": user.nickname,
            "avatar": user.avatar,
            "score": user.score,
            "status": user.status.value,
        }
    )