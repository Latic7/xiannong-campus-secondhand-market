from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps.auth import CurrentActor
from app.core.exceptions import (
    DuplicateConflictError,
    ForbiddenError,
    InvalidRequestError,
    ResourceNotFoundError,
    StateConflictError,
)
from app.core.status import ProductStatus
from app.crud import order as order_crud
from app.crud import product as product_crud
from app.schemas.products import ProductCreateRequest, ProductUpdateRequest
from app.services.storage import save_product_image, delete_product_image_file


def _require_product(db: Session, product_id: int, *, for_update: bool = False):
    product = product_crud.get_product(db, product_id, for_update=for_update)
    if product is None:
        raise ResourceNotFoundError("product not found", {"productId": product_id})
    return product


def _require_owner(product, actor: CurrentActor) -> None:
    if product.owner_id != actor.user_id:
        raise ForbiddenError("only product owner can perform this operation", {"productId": product.id})


def list_products(
    db: Session,
    page: int = 1,
    size: int = 20,
    keyword: str | None = None,
    sort: str | None = None,
    category_ids: list[int] | None = None,
    status_list: list[str] | None = None,
    owner_id: int | None = None,
) -> dict:
    page = max(page, 1)
    size = min(max(size, 1), 100)
    # 如果前端传了 status_list 则用指定的状态，否则走默认逻辑
    # 默认：公开列表显示已发布、已售出、已下架商品；owner 自己的列表显示所有状态
    if status_list is None:
        statuses = [ProductStatus.PUBLISHED.value, ProductStatus.SOLD.value] if owner_id is None else None
    else:
        # 公开列表不允许筛选 REMOVED（被驳回/下架的商品不对公众显示）
        if owner_id is None:
            status_list = [s for s in status_list if s != ProductStatus.REMOVED.value]
        statuses = status_list if status_list else None
    items, total = product_crud.list_products(db, page, size, keyword, sort, category_ids, status=statuses, owner_id=owner_id)
    return {
        "list": items,
        "page": {"page": page, "size": size, "total": total},
        "filters": {"keyword": keyword, "sort": sort, "categoryIds": category_ids, "status": status_list},
    }


def create_product(db: Session, payload: ProductCreateRequest, actor: CurrentActor) -> dict:
    product = product_crud.create_product(db, payload.model_dump(), actor.user_id)
    db.commit()
    db.refresh(product)
    return product_crud.serialize_product(db, product)


def get_product(db: Session, product_id: int) -> dict:
    product = _require_product(db, product_id)
    product_crud.increment_view_count(db, product)
    db.commit()
    db.refresh(product)
    return product_crud.serialize_product(db, product)


def update_product(db: Session, product_id: int, payload: ProductUpdateRequest, actor: CurrentActor) -> dict:
    product = _require_product(db, product_id, for_update=True)
    _require_owner(product, actor)
    changes = payload.model_dump(exclude_none=True)
    if not changes:
        return product_crud.serialize_product(db, product)
    if product.status == ProductStatus.SOLD.value:
        raise StateConflictError("sold products cannot be changed", {"productId": product_id})
    if changes.get("status") == ProductStatus.PUBLISHED.value:
        raise ForbiddenError("product publishing requires administrator review", {"productId": product_id})
    # 修改价格时仍受任何活跃订单（RESERVED/CONFIRMED）限制
    if "price" in changes and order_crud.get_active_order_for_product(db, product_id):
        raise StateConflictError("active order locks product price", {"productId": product_id})
    # 下架时仅受已确认订单（CONFIRMED）限制，允许已预约（RESERVED）时下架
    if changes.get("status") == ProductStatus.REMOVED.value and order_crud.has_confirmed_order_for_product(db, product_id):
        raise StateConflictError("confirmed order prevents product unlisting", {"productId": product_id})

    allowed_targets = {
        ProductStatus.DRAFT.value: {ProductStatus.PENDING.value, ProductStatus.REMOVED.value},
        ProductStatus.PENDING.value: {ProductStatus.REMOVED.value},
        ProductStatus.PUBLISHED.value: {ProductStatus.REMOVED.value},
        ProductStatus.REMOVED.value: {ProductStatus.PENDING.value},
        ProductStatus.REJECTED.value: set(),  # 终态，不可再变更
    }
    target = changes.get("status")
    if target and target != product.status and target not in allowed_targets.get(product.status, set()):
        raise StateConflictError("product state transition is not allowed", {"from": product.status, "to": target})

    product_crud.update_product(db, product, changes)
    db.commit()
    db.refresh(product)
    return product_crud.serialize_product(db, product)


def remove_product(db: Session, product_id: int, actor: CurrentActor) -> dict:
    product = _require_product(db, product_id, for_update=True)
    _require_owner(product, actor)
    if product.status == ProductStatus.REMOVED.value:
        return {"id": product_id, "deleted": True, "status": product.status}
    if product.status == ProductStatus.SOLD.value:
        raise StateConflictError("sold products cannot be unlisted", {"productId": product_id})
    # 仅已确认订单（CONFIRMED）阻止下架
    if order_crud.has_confirmed_order_for_product(db, product_id):
        raise StateConflictError("confirmed order prevents product unlisting", {"productId": product_id})
    # 取消所有已预约（RESERVED）订单
    reserved = order_crud.get_reserved_orders_for_product(db, product_id)
    cancelled_count = order_crud.cancel_orders_batch(db, reserved) if reserved else 0
    product_crud.update_product(db, product, {"status": ProductStatus.REMOVED.value})
    db.commit()
    return {"id": product_id, "deleted": True, "status": product.status, "cancelledOrders": cancelled_count}


def upload_product_image(
    db: Session,
    product_id: int,
    filename: str,
    content_type: str | None,
    content: bytes,
    actor: CurrentActor,
    base_url: str = "http://localhost:8000",
) -> dict:
    # 校验 product_id 为合法正整数，防止路径遍历
    if not isinstance(product_id, int) or product_id <= 0:
        raise InvalidRequestError("invalid product id")

    product = _require_product(db, product_id)
    _require_owner(product, actor)

    # 校验并保存图片到本地文件系统
    url, generated_name = save_product_image(product_id, filename, content_type, content)
    full_url = f"{base_url}{url}"

    try:
        image = product_crud.add_product_image(db, product_id, full_url)
        db.commit()
        db.refresh(image)
    except IntegrityError as exc:
        db.rollback()
        delete_product_image_file(url)
        raise DuplicateConflictError("product image already exists", {"productId": product_id}) from exc
    return {"id": image.id, "productId": product_id, "filename": generated_name, "url": full_url}


def delete_product_image(db: Session, product_id: int, image_id: int, actor: CurrentActor) -> dict:
    product = _require_product(db, product_id)
    _require_owner(product, actor)
    image = product_crud.get_product_image(db, product_id, image_id)
    if image is None:
        raise ResourceNotFoundError("product image not found", {"productId": product_id, "imageId": image_id})
    # 删除本地图片文件
    delete_product_image_file(image.url)
    product_crud.delete_product_image(db, image)
    db.commit()
    return {"productId": product_id, "imageId": image_id, "deleted": True}


def list_pending_products(db: Session, page: int = 1, size: int = 20, status: str | None = None) -> dict:
    page = max(page, 1)
    size = min(max(size, 1), 100)
    if status:
        # 支持逗号分隔的多个状态值
        status_filter = [s.strip() for s in status.split(",") if s.strip()]
    else:
        status_filter = ProductStatus.PENDING.value
    items, total = product_crud.list_products(
        db,
        page,
        size,
        status=status_filter,
    )
    return {"list": items, "page": {"page": page, "size": size, "total": total}}


def review_product(db: Session, product_id: int, result: str, reason: str | None = None) -> dict:
    product = _require_product(db, product_id, for_update=True)
    target = ProductStatus.PUBLISHED.value if result == "approved" else ProductStatus.REJECTED.value
    if product.status == target:
        return {"productId": product_id, "result": result, "reason": reason, "status": target}
    if product.status != ProductStatus.PENDING.value:
        raise StateConflictError(
            "only pending products can be reviewed",
            {"productId": product_id, "status": product.status},
        )
    product_crud.update_product(db, product, {"status": target})
    db.commit()
    return {"productId": product_id, "result": result, "reason": reason, "status": target}
