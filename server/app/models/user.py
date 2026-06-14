from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Enum, Index, String, Boolean, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
	__tablename__ = "users"
	__table_args__ = (
		Index("idx_users_status", "status"),
	)

	id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
	openid: Mapped[str | None] = mapped_column(String(64), unique=True)
	nickname: Mapped[str] = mapped_column(String(64), nullable=False)
	avatar: Mapped[str] = mapped_column(String(255), nullable=False, server_default="")
	score: Mapped[int] = mapped_column(nullable=False, server_default=text("100"))
	status: Mapped[str] = mapped_column(
		Enum("ACTIVE", "BANNED", name="user_status_enum"),
		nullable=False,
		server_default="ACTIVE",
	)
	is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("0"))  # 新增
	college: Mapped[str | None] = mapped_column(String(128))
	contact: Mapped[str | None] = mapped_column(String(64))
	created_at: Mapped[datetime] = mapped_column(
		DateTime,
		nullable=False,
		server_default=text("CURRENT_TIMESTAMP"),
	)
	updated_at: Mapped[datetime] = mapped_column(
		DateTime,
		nullable=False,
		server_default=text("CURRENT_TIMESTAMP"),
		server_onupdate=text("CURRENT_TIMESTAMP"),
	)