from fastapi import APIRouter

from app.core.response import api_ok
from app.schemas.common import TokenRefreshRequest, WxLoginRequest

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/wx-login")
def wx_login(payload: WxLoginRequest) -> dict:
    return api_ok(
        {
            "accessToken": "draft-access-token",
            "refreshToken": "draft-refresh-token",
            "expiresIn": 3600,
            "user": {
                "id": 1,
                "nickname": "Demo User",
                "avatar": "",
                "score": 100,
                "status": "active",
            },
            "wxCode": payload.code,
        }
    )


@router.post("/refresh")
def refresh_token(payload: TokenRefreshRequest) -> dict:
    return api_ok(
        {
            "accessToken": "new-draft-access-token",
            "refreshToken": payload.refreshToken,
            "expiresIn": 3600,
        }
    )


@router.post("/logout")
def logout() -> dict:
    return api_ok()


@router.get("/me")
def me() -> dict:
    return api_ok(
        {
            "id": 1,
            "nickname": "Demo User",
            "avatar": "",
            "score": 100,
            "status": "active",
        }
    )
