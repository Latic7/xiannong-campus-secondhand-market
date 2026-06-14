from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.settings import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.product import Product
from app.models.user import User


engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)


def override_get_db():
    with TestingSessionLocal() as db:
        yield db


def reset_backend_b_db() -> None:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with TestingSessionLocal() as db:
        db.add_all(
            [
                User(id=1, openid="owner", nickname="Owner"),
                User(id=2, openid="buyer", nickname="Buyer"),
                User(id=3, openid="other", nickname="Other"),
                User(id=10, openid="admin", nickname="Admin", is_admin=True),
            ]
        )
        db.add(
            Product(
                id=1001,
                owner_id=1,
                title="二手高数教材",
                description="九成新",
                price=Decimal("35.00"),
                category_id=1,
                status="published",
                favorite_count=0,
                view_count=0,
            )
        )
        db.commit()


def auth_header(user_id: int) -> dict[str, str]:
    token = jwt.encode(
        {
            "uid": user_id,
            "nickname": f"user-{user_id}",
            "typ": "access",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        },
        settings.JWT_SECRET,
        algorithm="HS256",
    )
    return {"Authorization": f"Bearer {token}"}


def install_db_override() -> None:
    app.dependency_overrides[get_db] = override_get_db


def clear_db_override() -> None:
    app.dependency_overrides.pop(get_db, None)
