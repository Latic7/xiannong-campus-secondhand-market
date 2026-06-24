from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, Index, Numeric, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Product(Base):
	__tablename__ = "products"
	__table_args__ = (
		Index("idx_products_status_created", "status", "created_at"),
		Index("idx_products_owner", "owner_id"),
		Index("idx_products_category", "category_id"),
		Index("idx_products_category_status_created", "category_id", "status", "created_at"),
	)

	id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
	owner_id: Mapped[int | None] = mapped_column(index=False)
	title: Mapped[str] = mapped_column(String(128), nullable=False)
	description: Mapped[str | None] = mapped_column(Text)
	price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
	category_id: Mapped[int | None] = mapped_column()
	status: Mapped[str] = mapped_column(
		Enum("DRAFT", "PENDING", "PUBLISHED", "REMOVED", "SOLD", "REJECTED", name="product_status_enum"),
		nullable=False,
		server_default="PENDING",
	)
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
	favorite_count: Mapped[int | None] = mapped_column(server_default=text("0"))
	view_count: Mapped[int | None] = mapped_column(server_default=text("0"))
