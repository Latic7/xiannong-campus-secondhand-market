from __future__ import annotations

from dataclasses import dataclass

import jwt
from fastapi import Header

from app.core.exceptions import AuthenticationError
from app.core.settings import settings


@dataclass(frozen=True)
class CurrentActor:
    user_id: int
    nickname: str = ""


def get_current_actor(authorization: str | None = Header(default=None)) -> CurrentActor:
    if not authorization or not authorization.startswith("Bearer "):
        raise AuthenticationError("missing bearer token")

    token = authorization.split(" ", 1)[1]
    try:
        token_data = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        raise AuthenticationError("access token invalid") from exc

    if token_data.get("typ") != "access" or not token_data.get("uid"):
        raise AuthenticationError("token type mismatch")
    return CurrentActor(user_id=int(token_data["uid"]), nickname=token_data.get("nickname", ""))
