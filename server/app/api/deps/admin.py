from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session
import jwt

from app.core.database import get_db
from app.core.settings import settings
from app.models.user import User


def get_current_admin(
    authorization: str = Header(...),
    db: Session = Depends(get_db),
) -> User:
    """
    获取当前管理员用户
    先验证 token，再从数据库查询用户并检查 is_admin 字段
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")
    
    token = authorization.split(" ", 1)[1]
    try:
        token_data = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="access token invalid")
    
    if token_data.get("typ") != "access":
        raise HTTPException(status_code=401, detail="token type mismatch")
    
    user = db.query(User).filter(User.id == token_data.get("uid")).first()
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    
    # 检查是否为管理员
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="admin permission required")
    
    return user