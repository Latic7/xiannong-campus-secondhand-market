from app.core.exceptions import ResourceNotFoundError, StateConflictError
from app.core.status import OrderStatus, ProductStatus
from app.crud import order as order_crud
from app.crud import product as product_crud
from app.schemas.orders import OrderCreateRequest, OrderReviewRequest


DEFAULT_BUYER_ID = 2


def create_order(payload: OrderCreateRequest) -> dict:
    product = product_crud.get_product(payload.productId)
    if product is None:
        raise ResourceNotFoundError("product not found", {"productId": payload.productId})
    if product["status"] != ProductStatus.PUBLISHED.value:
        raise StateConflictError(
            "product is not available for ordering",
            {"productId": payload.productId, "status": product["status"]},
        )
    if order_crud.has_active_order_for_product(payload.productId):
        raise StateConflictError("product already has an active order", {"productId": payload.productId})

    order = order_crud.create_order(
        product_id=payload.productId,
        buyer_id=DEFAULT_BUYER_ID,
        seller_id=product.get("ownerId"),
        amount=product["price"],
        remark=payload.remark,
    )
    # OpenAPI has no reserved product status; active-order checks prevent duplicate orders.
    return order


def get_order(order_id: int) -> dict:
    order = order_crud.get_order(order_id)
    if order is None:
        raise ResourceNotFoundError("order not found", {"orderId": order_id})
    return order


def seller_confirm(order_id: int) -> dict:
    order = get_order(order_id)
    if order["status"] == OrderStatus.CONFIRMED.value:
        return {"id": order_id, "status": OrderStatus.CONFIRMED.value}
    if order["status"] != OrderStatus.RESERVED.value:
        raise StateConflictError("order cannot be confirmed from current status", order)

    confirmed = order_crud.update_order_status(order_id, OrderStatus.CONFIRMED)
    return {"id": order_id, "status": confirmed["status"]}


def cancel_order(order_id: int) -> dict:
    order = get_order(order_id)
    if order["status"] == OrderStatus.CANCELLED.value:
        return {"id": order_id, "status": OrderStatus.CANCELLED.value}
    if order["status"] == OrderStatus.COMPLETED.value:
        raise StateConflictError("completed order cannot be cancelled", order)

    cancelled = order_crud.update_order_status(order_id, OrderStatus.CANCELLED)
    return {"id": order_id, "status": cancelled["status"]}


def complete_order(order_id: int) -> dict:
    order = get_order(order_id)
    if order["status"] == OrderStatus.COMPLETED.value:
        return {"id": order_id, "status": OrderStatus.COMPLETED.value}
    if order["status"] != OrderStatus.CONFIRMED.value:
        raise StateConflictError("order cannot be completed from current status", order)

    completed = order_crud.update_order_status(order_id, OrderStatus.COMPLETED)
    product_crud.update_product(order["productId"], {"status": ProductStatus.SOLD.value})
    return {"id": order_id, "status": completed["status"]}


def create_review(order_id: int, payload: OrderReviewRequest) -> dict:
    order = get_order(order_id)
    if order["status"] != OrderStatus.COMPLETED.value:
        raise StateConflictError("only completed orders can be reviewed", order)
    return order_crud.create_review(order_id, payload.score, payload.content)
