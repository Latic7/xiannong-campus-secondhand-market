from fastapi import APIRouter, Header, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import jwt

from app.core.response import api_ok, api_error
from app.core.settings import settings
from app.core.database import get_db
from app.models.user import User
from app.models.favorite import Favorite
from app.schemas.common import UserProfileUpdateRequest

router = APIRouter(prefix="/api/users", tags=["User"])


def _json_error(status_code: int, code: int, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=api_error(message=message, code=code),
    )


def _get_user_from_token(authorization: str | None) -> dict | JSONResponse:
    """从 token 解析用户基本信息，失败返回错误响应"""
    if not authorization or not authorization.startswith("Bearer "):
        return _json_error(401, 10030, "missing bearer token")
    
    token = authorization.split(" ", 1)[1]
    try:
        token_data = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        return _json_error(401, 10031, "access token invalid")
    
    if token_data.get("typ") != "access":
        return _json_error(401, 10032, "token type mismatch")
    
    return {
        "uid": token_data.get("uid", 0),
        "nickname": token_data.get("nickname", ""),
    }


@router.get("/me")
def get_profile(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db)
):
    """查询个人资料"""
    user_info = _get_user_from_token(authorization)
    if isinstance(user_info, JSONResponse):
        return user_info
    
    user = db.query(User).filter(User.id == user_info["uid"]).first()
    if not user:
        return _json_error(404, 10040, "user not found")
    
    # 统计收藏数量
    favorites_count = db.query(Favorite).filter(Favorite.user_id == user.id).count()
    
    return api_ok(
        {
            "id": user.id,
            "nickname": user.nickname,
            "avatar": user.avatar,
            "score": user.score,
            "status": user.status.value,
            "college": user.college,
            "contact": user.contact,
            "favorites": favorites_count,
        }
    )


@router.put("/me")
def update_profile(
    payload: UserProfileUpdateRequest,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db)
):
    """更新个人资料"""
    user_info = _get_user_from_token(authorization)
    if isinstance(user_info, JSONResponse):
        return user_info
    
    user = db.query(User).filter(User.id == user_info["uid"]).first()
    if not user:
        return _json_error(404, 10040, "user not found")
    
    # 更新字段（只更新传入的字段）
    if payload.nickname is not None:
        user.nickname = payload.nickname
    if payload.avatar is not None:
        user.avatar = payload.avatar
    if payload.college is not None:
        user.college = payload.college
    if payload.contact is not None:
        user.contact = payload.contact
    
    db.commit()
    db.refresh(user)
    
    updated = {}
    if payload.nickname is not None:
        updated["nickname"] = user.nickname
    if payload.avatar is not None:
        updated["avatar"] = user.avatar
    if payload.college is not None:
        updated["college"] = user.college
    if payload.contact is not None:
        updated["contact"] = user.contact
    
    return api_ok({"updated": True, "profile": updated})


@router.get("/me/favorites")
def list_favorites(
    page: int = 1,
    size: int = 20,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db)
):
    """查询收藏列表"""
    user_info = _get_user_from_token(authorization)
    if isinstance(user_info, JSONResponse):
        return user_info
    
    offset = (page - 1) * size
    
    # 查询收藏记录
    favorites = db.query(Favorite).filter(
        Favorite.user_id == user_info["uid"]
    ).offset(offset).limit(size).all()
    
    total = db.query(Favorite).filter(Favorite.user_id == user_info["uid"]).count()
    
    # 注意：这里只返回商品 ID 列表，商品详情由商品模块提供
    # 按照 OpenAPI 规范，收藏列表应返回商品信息
    # 由于商品模块不归您管，先返回商品 ID，联调时让前端根据 ID 获取详情
    favorite_list = [
        {
            "id": fav.id,
            "productId": fav.product_id,
            "createdAt": fav.created_at.isoformat() if fav.created_at else None,
        }
        for fav in favorites
    ]
    
    return api_ok({
        "list": favorite_list,
        "page": {
            "page": page,
            "size": size,
            "total": total
        }
    })


@router.post("/me/favorites/{product_id}")
def add_favorite(
    product_id: int,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db)
):
    """新增收藏"""
    user_info = _get_user_from_token(authorization)
    if isinstance(user_info, JSONResponse):
        return user_info
    
    # 检查是否已收藏
    existing = db.query(Favorite).filter(
        Favorite.user_id == user_info["uid"],
        Favorite.product_id == product_id
    ).first()
    
    if not existing:
        favorite = Favorite(
            user_id=user_info["uid"],
            product_id=product_id
        )
        db.add(favorite)
        db.commit()
    
    return api_ok({"productId": product_id, "favorited": True})


@router.delete("/me/favorites/{product_id}")
def remove_favorite(
    product_id: int,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db)
):
    """取消收藏"""
    user_info = _get_user_from_token(authorization)
    if isinstance(user_info, JSONResponse):
        return user_info
    
    favorite = db.query(Favorite).filter(
        Favorite.user_id == user_info["uid"],
        Favorite.product_id == product_id
    ).first()
    
    if favorite:
        db.delete(favorite)
        db.commit()
    
    return api_ok({"productId": product_id, "favorited": False})