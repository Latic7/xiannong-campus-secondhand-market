from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.settings import settings


_connect_args = {}
if settings.database_url.startswith("sqlite"):
	_connect_args = {"check_same_thread": False}

engine = create_engine(
	settings.database_url,
	future=True,
	pool_pre_ping=True,
	connect_args=_connect_args,
)

SessionLocal = sessionmaker(
	bind=engine,
	class_=Session,
	autocommit=False,
	autoflush=False,
	expire_on_commit=False,
)


def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()
