from fastapi import APIRouter

from app.core.response import api_ok
from app.schemas.common import UserProfileUpdateRequest

router = APIRouter(prefix="/api/users", tags=["User"])


@router.get("/me")
def get_profile() -> dict:
    return api_ok(
        {
            "id": 1,
            "nickname": "Demo User",
            "avatar": "",
            "score": 100,
            "status": "active",
            "favorites": 0,
        }
    )


@router.put("/me")
def update_profile(payload: UserProfileUpdateRequest) -> dict:
    return api_ok({"updated": True, "profile": payload.model_dump()})


@router.get("/me/favorites")
def list_favorites(page: int = 1, size: int = 20) -> dict:
    return api_ok({"list": [], "page": {"page": page, "size": size, "total": 0}})


@router.post("/me/favorites/{product_id}")
def add_favorite(product_id: int) -> dict:
    return api_ok({"productId": product_id, "favorited": True})


@router.delete("/me/favorites/{product_id}")
def remove_favorite(product_id: int) -> dict:
    return api_ok({"productId": product_id, "favorited": False})
