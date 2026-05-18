from datetime import datetime, timedelta, timezone
import hashlib

from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse
import httpx
import jwt

from app.core.response import api_error, api_ok
from app.core.settings import settings
from app.schemas.common import TokenRefreshRequest, WxLoginRequest

router = APIRouter(prefix="/api/auth", tags=["Auth"])


def _issue_token(payload: dict, expires_seconds: int) -> str:
    expire_at = datetime.now(timezone.utc) + timedelta(seconds=expires_seconds)
    token_payload = {**payload, "exp": expire_at}
    return jwt.encode(token_payload, settings.jwt_secret, algorithm="HS256")


def _wechat_code_to_session(code: str) -> dict:
    response = httpx.get(
        "https://api.weixin.qq.com/sns/jscode2session",
        params={
            "appid": settings.wechat_app_id,
            "secret": settings.wechat_app_secret,
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
def wx_login(payload: WxLoginRequest):
    if not settings.wechat_app_id or not settings.wechat_app_secret:
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

    user_id = int(hashlib.sha256(openid.encode("utf-8")).hexdigest()[:8], 16)
    profile = {
        "id": user_id,
        "nickname": f"WX_{openid[-6:]}",
        "avatar": "",
        "score": 100,
        "status": "active",
    }

    access_token = _issue_token(
        {
            "sub": openid,
            "uid": user_id,
            "nickname": profile["nickname"],
            "typ": "access",
        },
        settings.jwt_expires_seconds,
    )
    refresh_token = _issue_token(
        {
            "sub": openid,
            "uid": user_id,
            "nickname": profile["nickname"],
            "typ": "refresh",
        },
        settings.jwt_refresh_expires_seconds,
    )

    return api_ok(
        {
            "accessToken": access_token,
            "refreshToken": refresh_token,
            "expiresIn": settings.jwt_expires_seconds,
            "user": profile,
        }
    )


@router.post("/refresh")
def refresh_token(payload: TokenRefreshRequest):
    try:
        token_data = jwt.decode(payload.refreshToken, settings.jwt_secret, algorithms=["HS256"])
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
        settings.jwt_expires_seconds,
    )

    return api_ok(
        {
            "accessToken": new_access_token,
            "refreshToken": payload.refreshToken,
            "expiresIn": settings.jwt_expires_seconds,
        }
    )


@router.post("/logout")
def logout() -> dict:
    return api_ok()


@router.get("/me")
def me(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        return _json_error(status_code=401, code=10030, message="missing bearer token")

    token = authorization.split(" ", 1)[1]
    try:
        token_data = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except jwt.PyJWTError:
        return _json_error(status_code=401, code=10031, message="access token invalid")

    if token_data.get("typ") != "access":
        return _json_error(status_code=401, code=10032, message="token type mismatch")

    return api_ok(
        {
            "id": token_data.get("uid", 0),
            "nickname": token_data.get("nickname", "WX_USER"),
            "avatar": "",
            "score": 100,
            "status": "active",
        }
    )
