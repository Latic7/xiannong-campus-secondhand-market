from copy import deepcopy
from datetime import datetime, timedelta, timezone

from app.core.status import OrderStatus


def _now() -> datetime:
    return datetime.now(timezone.utc)


_orders: dict[int, dict] = {}
_reviews: list[dict] = []
_next_order_id = 5001


def create_order(
    product_id: int,
    buyer_id: int | None,
    seller_id: int | None,
    amount: float,
    remark: str | None = None,
) -> dict:
    global _next_order_id
    order_id = _next_order_id
    _next_order_id += 1
    created_at = _now()
    order = {
        "id": order_id,
        "productId": product_id,
        "buyerId": buyer_id,
        "sellerId": seller_id,
        "amount": float(amount),
        "remark": remark,
        "status": OrderStatus.RESERVED.value,
        "createdAt": created_at.isoformat(),
        "expireAt": (created_at + timedelta(hours=48)).isoformat(),
    }
    _orders[order_id] = order
    return deepcopy(order)


def has_active_order_for_product(product_id: int) -> bool:
    return any(
        order["productId"] == product_id
        and order["status"] in {OrderStatus.RESERVED.value, OrderStatus.CONFIRMED.value}
        for order in _orders.values()
    )


def get_order(order_id: int) -> dict | None:
    order = _orders.get(order_id)
    return deepcopy(order) if order else None


def update_order_status(order_id: int, status: OrderStatus) -> dict | None:
    order = _orders.get(order_id)
    if order is None:
        return None
    order["status"] = status.value
    return deepcopy(order)


def create_review(order_id: int, score: int, content: str) -> dict:
    review = {"orderId": order_id, "score": score, "content": content}
    _reviews.append(review)
    return deepcopy(review)
