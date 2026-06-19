from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.product import Product
from app.models.product_image import ProductImage
from app.models.review import Review


ACTIVE_ORDER_STATUSES = ("RESERVED", "CONFIRMED")


def serialize_order(order: Order) -> dict:
    return {
        "id": order.id,
        "productId": order.product_id,
        "buyerId": order.buyer_id,
        "sellerId": order.seller_id,
        "amount": float(order.amount) if order.amount is not None else None,
        "remark": order.remark,
        "status": order.status,
        "createdAt": order.created_at.isoformat() if order.created_at else None,
        "expireAt": order.expire_at.isoformat() if order.expire_at else None,
    }


def _product_summary(db: Session, product_id: int) -> dict | None:
    product = db.get(Product, product_id)
    if product is None:
        return None
    image = db.scalar(
        select(ProductImage.url)
        .where(ProductImage.product_id == product_id)
        .order_by(ProductImage.id)
        .limit(1)
    )
    return {
        "id": product.id,
        "title": product.title,
        "price": float(product.price) if product.price is not None else None,
        "image": image or "",
        "status": product.status,
    }


def serialize_order_with_product(db: Session, order: Order) -> dict:
    data = serialize_order(order)
    data["product"] = _product_summary(db, order.product_id)
    return data


def create_order(
    db: Session,
    product_id: int,
    buyer_id: int,
    seller_id: int | None,
    amount: Decimal,
    remark: str | None = None,
) -> Order:
    order = Order(
        product_id=product_id,
        buyer_id=buyer_id,
        seller_id=seller_id,
        amount=amount,
        remark=remark,
        status="RESERVED",
        expire_at=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=48),
    )
    db.add(order)
    db.flush()
    return order


def get_order(db: Session, order_id: int, *, for_update: bool = False) -> Order | None:
    statement = select(Order).where(Order.id == order_id)
    if for_update:
        statement = statement.with_for_update()
    return db.scalar(statement)


def list_orders(
    db: Session,
    user_id: int,
    page: int = 1,
    size: int = 20,
    role: str | None = None,
    status: str | None = None,
) -> tuple[list[dict], int]:
    statement = select(Order)
    if role == "buyer":
        statement = statement.where(Order.buyer_id == user_id)
    elif role == "seller":
        statement = statement.where(Order.seller_id == user_id)
    else:
        statement = statement.where(or_(Order.buyer_id == user_id, Order.seller_id == user_id))
    if status:
        statement = statement.where(Order.status == status)

    total = db.scalar(select(func.count()).select_from(statement.subquery())) or 0
    rows = db.scalars(
        statement.order_by(Order.created_at.desc(), Order.id.desc())
        .offset((page - 1) * size)
        .limit(size)
    ).all()
    return [serialize_order_with_product(db, order) for order in rows], int(total)


def get_active_order_for_product(db: Session, product_id: int) -> Order | None:
    return db.scalar(
        select(Order)
        .where(Order.product_id == product_id, Order.status.in_(ACTIVE_ORDER_STATUSES))
        .order_by(Order.id)
        .limit(1)
    )


def update_order_status(db: Session, order: Order, status: str) -> Order:
    order.status = status
    db.flush()
    return order


def get_review_for_order_and_reviewer(db: Session, order_id: int, reviewer_id: int) -> Review | None:
    return db.scalar(select(Review).where(Review.order_id == order_id, Review.reviewer_id == reviewer_id))


def create_review(db: Session, order: Order, reviewer_id: int, score: int, content: str) -> Review:
    review = Review(
        order_id=order.id,
        product_id=order.product_id,
        reviewer_id=reviewer_id,
        reviewee_id=order.seller_id,
        score=score,
        content=content,
    )
    db.add(review)
    db.flush()
    return review


def serialize_review(review: Review) -> dict:
    return {
        "id": review.id,
        "orderId": review.order_id,
        "productId": review.product_id,
        "reviewerId": review.reviewer_id,
        "revieweeId": review.reviewee_id,
        "score": review.score,
        "content": review.content,
        "createdAt": review.created_at.isoformat() if review.created_at else None,
    }
