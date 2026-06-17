from typing import Literal

from pydantic import BaseModel, Field


OrderStatusValue = Literal["CREATED", "RESERVED", "CONFIRMED", "COMPLETED", "CANCELLED"]


class OrderCreateRequest(BaseModel):
    productId: int
    remark: str | None = Field(default=None, max_length=255)


class OrderReviewRequest(BaseModel):
    score: int = Field(ge=1, le=5)
    content: str = Field(min_length=1, max_length=500)


class Order(BaseModel):
    id: int
    productId: int
    buyerId: int | None = None
    sellerId: int | None = None
    amount: float | None = None
    remark: str | None = None
    status: OrderStatusValue
    createdAt: str | None = None
    expireAt: str | None = None
