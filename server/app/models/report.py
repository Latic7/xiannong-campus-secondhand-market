from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Enum, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Report(Base):
	__tablename__ = "reports"
	__table_args__ = (
		Index("idx_reports_status_created", "status", "created_at"),
		Index("idx_reports_target", "target_type", "target_id"),
	)

	id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
	reporter_id: Mapped[int | None] = mapped_column()
	target_type: Mapped[str] = mapped_column(
		Enum("product", "user", "order", name="report_target_type_enum"),
		nullable=False,
	)
	target_id: Mapped[int] = mapped_column(nullable=False)
	reason: Mapped[str] = mapped_column(String(255), nullable=False)
	status: Mapped[str] = mapped_column(
		Enum("open", "rejected", "handled", name="report_status_enum"),
		nullable=False,
		server_default="open",
	)
	assignee_id: Mapped[int | None] = mapped_column()
	handle_action: Mapped[str | None] = mapped_column(String(32))
	handle_reason: Mapped[str | None] = mapped_column(String(255))
	created_at: Mapped[datetime] = mapped_column(
		DateTime,
		nullable=False,
		server_default=text("CURRENT_TIMESTAMP"),
	)
	handled_at: Mapped[datetime | None] = mapped_column(DateTime)
