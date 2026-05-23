from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AdminLog(Base):
	__tablename__ = "admin_logs"
	__table_args__ = (
		Index("idx_admin_logs_actor", "actor_id"),
		Index("idx_admin_logs_created", "created_at"),
		Index("idx_admin_logs_target", "target_type", "target_id"),
	)

	id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
	actor_id: Mapped[int] = mapped_column(nullable=False)
	action: Mapped[str] = mapped_column(String(32), nullable=False)
	target_type: Mapped[str] = mapped_column(String(32), nullable=False)
	target_id: Mapped[int] = mapped_column(nullable=False)
	remark: Mapped[str | None] = mapped_column(String(255))
	created_at: Mapped[datetime] = mapped_column(
		DateTime,
		nullable=False,
		server_default=text("CURRENT_TIMESTAMP"),
	)
