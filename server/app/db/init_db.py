from __future__ import annotations

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app import models  # noqa: F401  # ensure model metadata is loaded


def init_db() -> None:
	Base.metadata.create_all(bind=engine)


def reset_db() -> None:
	Base.metadata.drop_all(bind=engine)
	Base.metadata.create_all(bind=engine)
