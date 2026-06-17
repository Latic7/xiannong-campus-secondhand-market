from __future__ import annotations

from collections import defaultdict
from threading import Lock

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps.auth import CurrentActor
from app.core.exceptions import DuplicateConflictError, ForbiddenError, ResourceNotFoundError, StateConflictError
from app.core.status import OrderStatus, ProductStatus
from app.crud import order as order_crud
from app.crud import product as product_crud
from app.schemas.orders import OrderCreateRequest, OrderReviewRequest


_product_order_locks: defaultdict[int, Lock] = defaultdict(Lock)


def _require_order(db: Session, order_id: int, *, for_update: bool = False):
    order = order_crud.get_order(db, order_id, for_update=for_update)
    if order is None:
        raise ResourceNotFoundError("order not found", {"orderId": order_id})
    return order


def _require_related(order, actor: CurrentActor) -> None:
    if actor.user_id not in {order.buyer_id, order.seller_id}:
        raise ForbiddenError("only order participants can perform this operation", {"orderId": order.id})


def create_order(db: Session, payload: OrderCreateRequest, actor: CurrentActor) -> dict:
    # The process lock protects SQLite/tests and single-worker retries; the row
    # lock below remains the cross-process authority on MySQL.
    with _product_order_locks[payload.productId]:
        try:
            product = product_crud.get_product(db, payload.productId, for_update=True)
            if product is None:
                raise ResourceNotFoundError("product not found", {"productId": payload.productId})
            if product.owner_id == actor.user_id:
                raise StateConflictError("product owner cannot buy own product", {"productId": payload.productId})
            if product.status != ProductStatus.PUBLISHED.value:
                raise StateConflictError("product is not available for ordering", {"productId": payload.productId})
            if order_crud.get_active_order_for_product(db, payload.productId):
                raise DuplicateConflictError("product already has an active order", {"productId": payload.productId})
            order = order_crud.create_order(db, product.id, actor.user_id, product.owner_id, product.price, payload.remark)
            db.commit()
            db.refresh(order)
            return order_crud.serialize_order(order)
        except Exception:
            db.rollback()
            raise


def get_order(db: Session, order_id: int, actor: CurrentActor) -> dict:
    order = _require_order(db, order_id)
    _require_related(order, actor)
    return order_crud.serialize_order(order)


def seller_confirm(db: Session, order_id: int, actor: CurrentActor) -> dict:
    order = _require_order(db, order_id, for_update=True)
    if order.seller_id != actor.user_id:
        raise ForbiddenError("only seller can confirm order", {"orderId": order_id})
    if order.status == OrderStatus.CONFIRMED.value:
        return {"id": order_id, "status": order.status}
    if order.status != OrderStatus.RESERVED.value:
        raise StateConflictError("order cannot be confirmed from current status", {"orderId": order_id, "status": order.status})
    order_crud.update_order_status(db, order, OrderStatus.CONFIRMED.value)
    db.commit()
    return {"id": order_id, "status": order.status}


def cancel_order(db: Session, order_id: int, actor: CurrentActor) -> dict:
    order = _require_order(db, order_id, for_update=True)
    _require_related(order, actor)
    if order.status == OrderStatus.CANCELLED.value:
        return {"id": order_id, "status": order.status}
    if order.status not in {OrderStatus.RESERVED.value, OrderStatus.CONFIRMED.value}:
        raise StateConflictError("order cannot be cancelled from current status", {"orderId": order_id, "status": order.status})
    order_crud.update_order_status(db, order, OrderStatus.CANCELLED.value)
    db.commit()
    return {"id": order_id, "status": order.status}


def complete_order(db: Session, order_id: int, actor: CurrentActor) -> dict:
    order = _require_order(db, order_id, for_update=True)
    if order.buyer_id != actor.user_id:
        raise ForbiddenError("only buyer can complete order", {"orderId": order_id})
    if order.status == OrderStatus.COMPLETED.value:
        return {"id": order_id, "status": order.status}
    if order.status != OrderStatus.CONFIRMED.value:
        raise StateConflictError("order cannot be completed from current status", {"orderId": order_id, "status": order.status})
    product = product_crud.get_product(db, order.product_id, for_update=True)
    if product is None:
        raise ResourceNotFoundError("product not found", {"productId": order.product_id})
    order_crud.update_order_status(db, order, OrderStatus.COMPLETED.value)
    product_crud.update_product(db, product, {"status": ProductStatus.SOLD.value})
    db.commit()
    return {"id": order_id, "status": order.status}


def create_review(db: Session, order_id: int, payload: OrderReviewRequest, actor: CurrentActor) -> dict:
    order = _require_order(db, order_id, for_update=True)
    if order.buyer_id != actor.user_id:
        raise ForbiddenError("only buyer can review order", {"orderId": order_id})
    if order.status != OrderStatus.COMPLETED.value:
        raise StateConflictError("only completed orders can be reviewed", {"orderId": order_id, "status": order.status})
    if order_crud.get_review_for_order_and_reviewer(db, order_id, actor.user_id):
        raise DuplicateConflictError("order already reviewed", {"orderId": order_id})
    try:
        review = order_crud.create_review(db, order, actor.user_id, payload.score, payload.content)
        db.commit()
        db.refresh(review)
        return order_crud.serialize_review(review)
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateConflictError("order already reviewed", {"orderId": order_id}) from exc
