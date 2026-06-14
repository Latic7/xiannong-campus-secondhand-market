from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, Index, Numeric, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Order(Base):
	__tablename__ = "orders"
	__table_args__ = (
		Index("idx_orders_status_created", "status", "created_at"),
		Index("idx_orders_buyer", "buyer_id"),
		Index("idx_orders_seller", "seller_id"),
		Index("idx_orders_product", "product_id"),
		Index("idx_orders_product_status", "product_id", "status"),
	)

	id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
	product_id: Mapped[int] = mapped_column(nullable=False)
	buyer_id: Mapped[int | None] = mapped_column()
	seller_id: Mapped[int | None] = mapped_column()
	amount: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
	remark: Mapped[str | None] = mapped_column(String(255))
	status: Mapped[str] = mapped_column(
		Enum("created", "reserved", "confirmed", "completed", "cancelled", name="order_status_enum"),
		nullable=False,
		server_default="created",
	)
	created_at: Mapped[datetime] = mapped_column(
		DateTime,
		nullable=False,
		server_default=text("CURRENT_TIMESTAMP"),
	)
	expire_at: Mapped[datetime | None] = mapped_column(DateTime)
