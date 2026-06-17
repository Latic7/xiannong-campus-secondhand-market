from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Index, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (
        UniqueConstraint("order_id", "reviewer_id", name="uq_reviews_order_reviewer"),
        Index("idx_reviews_order", "order_id"),
        Index("idx_reviews_product", "product_id"),
        Index("idx_reviews_reviewer", "reviewer_id"),
        Index("idx_reviews_reviewee", "reviewee_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(nullable=False)
    product_id: Mapped[int] = mapped_column(nullable=False)
    reviewer_id: Mapped[int] = mapped_column(nullable=False)
    reviewee_id: Mapped[int | None] = mapped_column()
    score: Mapped[int] = mapped_column(nullable=False)
    content: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
