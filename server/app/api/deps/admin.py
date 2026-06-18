from fastapi import Depends, Header
from sqlalchemy.orm import Session
import jwt

from app.core.database import get_db
from app.core.settings import settings
from app.models.user import User
from app.core.exceptions import (
    BusinessError,
    UnauthorizedError,
    PermissionDeniedError,
    TokenInvalidError,
)


def get_current_admin(
    authorization: str = Header(...),
    db: Session = Depends(get_db),
) -> dict:
    """
    获取当前管理员用户信息
    校验 token 并检查 is_admin 字段
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedError(message="missing bearer token")
    
    token = authorization.split(" ", 1)[1]
    try:
        token_data = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise TokenInvalidError(message="access token invalid")
    
    if token_data.get("typ") != "access":
        raise TokenInvalidError(message="token type mismatch")
    
    user = db.scalar(select(User).where(User.id == token_data.get("uid")))
    if not user:
        raise BusinessError(code=10033, message="user not found", status_code=404)
    
    if not user.is_admin:
        raise PermissionDeniedError(message="admin permission required")
    
    return {
        "id": user.id,
        "openid": user.openid,
        "nickname": user.nickname,
        "is_admin": user.is_admin,
    }