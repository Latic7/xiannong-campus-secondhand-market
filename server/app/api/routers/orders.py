from fastapi import APIRouter

from app.core.response import api_ok
from app.core.status import OrderStatus
from app.schemas.common import OrderCreateRequest, OrderReviewRequest

router = APIRouter(prefix="/api/orders", tags=["Order"])


@router.post("")
def create_order(payload: OrderCreateRequest) -> dict:
    return api_ok(
        {
            "id": 5001,
            "productId": payload.productId,
            "status": OrderStatus.CREATED.value,
            "remark": payload.remark,
        }
    )


@router.get("/{order_id}")
def get_order(order_id: int) -> dict:
    return api_ok({"id": order_id, "status": OrderStatus.CREATED.value})


@router.post("/{order_id}/seller-confirm")
def seller_confirm(order_id: int) -> dict:
    return api_ok({"id": order_id, "status": OrderStatus.CONFIRMED.value})


@router.post("/{order_id}/cancel")
def cancel_order(order_id: int) -> dict:
    return api_ok({"id": order_id, "status": OrderStatus.CANCELLED.value})


@router.post("/{order_id}/complete")
def complete_order(order_id: int) -> dict:
    return api_ok({"id": order_id, "status": OrderStatus.COMPLETED.value})


@router.post("/{order_id}/reviews")
def create_review(order_id: int, payload: OrderReviewRequest) -> dict:
    return api_ok(order_service.create_review(order_id, payload))
