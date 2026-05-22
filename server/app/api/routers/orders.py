from fastapi import APIRouter

from app.core.response import api_ok
from app.schemas.orders import OrderCreateRequest, OrderReviewRequest
from app.services import order_service

router = APIRouter(prefix="/api/orders", tags=["Order"])


@router.post("")
def create_order(payload: OrderCreateRequest) -> dict:
    return api_ok(order_service.create_order(payload))


@router.get("/{order_id}")
def get_order(order_id: int) -> dict:
    return api_ok(order_service.get_order(order_id))


@router.post("/{order_id}/seller-confirm")
def seller_confirm(order_id: int) -> dict:
    return api_ok(order_service.seller_confirm(order_id))


@router.post("/{order_id}/cancel")
def cancel_order(order_id: int) -> dict:
    return api_ok(order_service.cancel_order(order_id))


@router.post("/{order_id}/complete")
def complete_order(order_id: int) -> dict:
    return api_ok(order_service.complete_order(order_id))


@router.post("/{order_id}/reviews")
def create_review(order_id: int, payload: OrderReviewRequest) -> dict:
    return api_ok(order_service.create_review(order_id, payload))
