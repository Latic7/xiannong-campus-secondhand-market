from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Header, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import httpx
import jwt

from app.core.response import api_error, api_ok
from app.core.settings import settings
from app.core.database import get_db
from app.models.user import User
from app.schemas.common import TokenRefreshRequest, WxLoginRequest

router = APIRouter(prefix="/api/auth", tags=["Auth"])


def _issue_token(payload: dict, expires_seconds: int) -> str:
    expire_at = datetime.now(timezone.utc) + timedelta(seconds=expires_seconds)
    token_payload = {**payload, "exp": expire_at}
    return jwt.encode(token_payload, settings.JWT_SECRET, algorithm="HS256")


def _wechat_code_to_session(code: str) -> dict:
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
def wx_login(payload: WxLoginRequest, db: Session = Depends(get_db)):
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

    user = db.query(User).filter(User.openid == openid).first()

    if not user:
        user = User(
            openid=openid,
            nickname=f"WX_{openid[-6:]}",
            avatar="",
            score=100,
            status="active",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    profile = {
        "id": user.id,
        "nickname": user.nickname,
        "avatar": user.avatar,
        "score": user.score,
        "status": user.status,
    }

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
    return api_ok()


@router.get("/me")
def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    if not authorization or not authorization.startswith("Bearer "):
        return _json_error(status_code=401, code=10030, message="missing bearer token")

    token = authorization.split(" ", 1)[1]
    try:
        token_data = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        return _json_error(status_code=401, code=10031, message="access token invalid")

    if token_data.get("typ") != "access":
        return _json_error(status_code=401, code=10032, message="token type mismatch")

    user = db.query(User).filter(User.id == token_data.get("uid")).first()
    if not user:
        return _json_error(status_code=404, code=10033, message="user not found")

    return api_ok(
        {
            "id": user.id,
            "nickname": user.nickname,
            "avatar": user.avatar,
            "score": user.score,
            "status": user.status,
        }
    )