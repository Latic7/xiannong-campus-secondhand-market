from __future__ import annotations

from dataclasses import dataclass

import jwt
from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import AuthenticationError, ForbiddenError
from app.core.settings import settings
from app.models.user import User


@dataclass(frozen=True)
class CurrentActor:
    user_id: int
    nickname: str = ""


def get_current_actor(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> CurrentActor:
    if not authorization or not authorization.startswith("Bearer "):
        raise AuthenticationError("missing bearer token")

    token = authorization.split(" ", 1)[1]
    try:
        token_data = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        raise AuthenticationError("access token invalid") from exc

    if token_data.get("typ") != "access" or not token_data.get("uid"):
        raise AuthenticationError("token type mismatch")

    user_id = int(token_data["uid"])
    # 检查用户是否被封禁
    user = db.get(User, user_id)
    if user and user.status == "BANNED":
        raise ForbiddenError("账户已被封禁，请联系后端管理员解封")

    return CurrentActor(user_id=user_id, nickname=token_data.get("nickname", ""))
