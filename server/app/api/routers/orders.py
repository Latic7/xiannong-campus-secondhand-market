from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps.auth import CurrentActor, get_current_actor
from app.core.response import api_ok
from app.core.database import get_db
from app.schemas.orders import OrderCreateRequest, OrderReviewRequest
from app.services import order_service

router = APIRouter(prefix="/api/orders", tags=["Order"])


@router.get("")
def list_orders(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    role: str | None = Query(None, description="buyer, seller, or omitted for all related orders"),
    status: str | None = None,
    db: Session = Depends(get_db),
    actor: CurrentActor = Depends(get_current_actor),
) -> dict:
    return api_ok(order_service.list_orders(db, actor, page=page, size=size, role=role, status=status))


@router.post("")
def create_order(
    payload: OrderCreateRequest,
    db: Session = Depends(get_db),
    actor: CurrentActor = Depends(get_current_actor),
) -> dict:
    return api_ok(order_service.create_order(db, payload, actor))


@router.get("/{order_id}")
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    actor: CurrentActor = Depends(get_current_actor),
) -> dict:
    return api_ok(order_service.get_order(db, order_id, actor))


@router.post("/{order_id}/seller-confirm")
def seller_confirm(
    order_id: int,
    db: Session = Depends(get_db),
    actor: CurrentActor = Depends(get_current_actor),
) -> dict:
    return api_ok(order_service.seller_confirm(db, order_id, actor))


@router.post("/{order_id}/cancel")
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    actor: CurrentActor = Depends(get_current_actor),
) -> dict:
    return api_ok(order_service.cancel_order(db, order_id, actor))


@router.post("/{order_id}/complete")
def complete_order(
    order_id: int,
    db: Session = Depends(get_db),
    actor: CurrentActor = Depends(get_current_actor),
) -> dict:
    return api_ok(order_service.complete_order(db, order_id, actor))


@router.post("/{order_id}/reviews")
def create_review(
    order_id: int,
    payload: OrderReviewRequest,
    db: Session = Depends(get_db),
    actor: CurrentActor = Depends(get_current_actor),
) -> dict:
    return api_ok(order_service.create_review(db, order_id, payload, actor))
