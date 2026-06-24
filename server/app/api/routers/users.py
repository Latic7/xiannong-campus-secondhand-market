from typing import Optional

from fastapi import APIRouter, Header, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.response import api_ok, api_error
from app.core.settings import settings
from app.core.database import get_db
from app.services.user_service import UserService
from app.schemas.common import UserProfileUpdateRequest

router = APIRouter(prefix="/api/users", tags=["User"])


def _json_error(status_code: int, code: int, message: str) -> JSONResponse:
    """统一错误响应"""
    return JSONResponse(
        status_code=status_code,
        content=api_error(message=message, code=code),
    )


def _get_user_id_from_token(authorization: Optional[str]) -> tuple[Optional[int], Optional[JSONResponse]]:
    """
    从 token 解析用户 ID
    返回: (user_id, 错误响应)
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None, _json_error(401, 10030, "missing bearer token")
    
    token = authorization.split(" ", 1)[1]
    try:
        import jwt
        token_data = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    except Exception:
        return None, _json_error(401, 10031, "access token invalid")
    
    if token_data.get("typ") != "access":
        return None, _json_error(401, 10032, "token type mismatch")
    
    return token_data.get("uid", 0), None


@router.get("/me")
def get_profile(
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db)
):
    """查询个人资料"""
    user_id, error = _get_user_id_from_token(authorization)
    if error:
        return error
    
    user_service = UserService(db)
    profile = user_service.get_user_profile(user_id)
    
    if not profile:
        return _json_error(404, 10040, "user not found")
    
    return api_ok(profile)


@router.put("/me")
def update_profile(
    payload: UserProfileUpdateRequest,
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db)
):
    """更新个人资料"""
    user_id, error = _get_user_id_from_token(authorization)
    if error:
        return error
    
    user_service = UserService(db)
    success, user, updated_fields = user_service.update_profile(
        user_id=user_id,
        nickname=payload.nickname,
        avatar=payload.avatar,
        college=payload.college,
        contact=payload.contact
    )
    
    if not success:
        return _json_error(404, 10040, "user not found")
    
    return api_ok({"updated": True, "profile": updated_fields})


@router.get("/me/favorites")
def list_favorites(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    size: int = Query(20, ge=1, le=100, description="每页数量，最大100"),
    keyword: str | None = Query(None, description="模糊搜索关键词"),
    sort: str | None = Query(None, description="排序表达式"),
    categoryIds: str | None = Query(None, description="分类ID，多个用逗号分隔"),
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db)
):
    """查询收藏列表"""
    user_id, error = _get_user_id_from_token(authorization)
    if error:
        return error
    
    # 解析多分类
    cat_ids = None
    if categoryIds:
        try:
            cat_ids = [int(c.strip()) for c in categoryIds.split(",") if c.strip()]
        except ValueError:
            pass
    
    user_service = UserService(db)
    favorite_list, total = user_service.get_favorites(
        user_id, page, size,
        keyword=keyword, sort=sort, category_ids=cat_ids
    )
    
    return api_ok({
        "list": favorite_list,
        "page": {
            "page": page,
            "size": size,
            "total": total
        },
        "filters": {"keyword": keyword, "sort": sort, "categoryIds": cat_ids},
    })


@router.post("/me/favorites/{product_id}")
def add_favorite(
    product_id: int,
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db)
):
    """新增收藏"""
    user_id, error = _get_user_id_from_token(authorization)
    if error:
        return error
    
    user_service = UserService(db)
    added = user_service.add_favorite(user_id, product_id)
    
    return api_ok({"productId": product_id, "favorited": added})


@router.delete("/me/favorites/{product_id}")
def remove_favorite(
    product_id: int,
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db)
):
    """取消收藏"""
    user_id, error = _get_user_id_from_token(authorization)
    if error:
        return error
    
    user_service = UserService(db)
    removed = user_service.remove_favorite(user_id, product_id)
    
    return api_ok({"productId": product_id, "favorited": not removed})