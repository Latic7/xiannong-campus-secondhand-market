from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class StatsDaily(Base):
    __tablename__ = "stats_daily"
    __table_args__ = (UniqueConstraint("stat_date", name="uq_stats_daily_date"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    stat_date: Mapped[date] = mapped_column(Date, nullable=False)
    users: Mapped[int] = mapped_column(nullable=False, server_default=text("0"))
    products: Mapped[int] = mapped_column(nullable=False, server_default=text("0"))
    orders: Mapped[int] = mapped_column(nullable=False, server_default=text("0"))
    reports: Mapped[int] = mapped_column(nullable=False, server_default=text("0"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )