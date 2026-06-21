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
from app.services.storage import get_image_storage, validate_and_save_image


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
    category_id: int | None = None,
    owner_id: int | None = None,
) -> dict:
    page = max(page, 1)
    size = min(max(size, 1), 100)
    # 公开列表只显示已发布或已售出商品；owner 自己的列表显示所有状态
    statuses = [ProductStatus.PUBLISHED.value, ProductStatus.SOLD.value] if owner_id is None else None
    items, total = product_crud.list_products(db, page, size, keyword, sort, category_id, status=statuses, owner_id=owner_id)
    return {
        "list": items,
        "page": {"page": page, "size": size, "total": total},
        "filters": {"keyword": keyword, "sort": sort, "categoryId": category_id},
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
    if ("price" in changes or changes.get("status") == ProductStatus.REMOVED.value) and order_crud.get_active_order_for_product(
        db, product_id
    ):
        raise StateConflictError("active order locks product price and availability", {"productId": product_id})

    allowed_targets = {
        ProductStatus.DRAFT.value: {ProductStatus.PENDING.value, ProductStatus.REMOVED.value},
        ProductStatus.PENDING.value: {ProductStatus.REMOVED.value},
        ProductStatus.PUBLISHED.value: {ProductStatus.REMOVED.value},
        ProductStatus.REMOVED.value: {ProductStatus.PENDING.value},
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
    if order_crud.get_active_order_for_product(db, product_id):
        raise StateConflictError("active order prevents product unlisting", {"productId": product_id})
    product_crud.update_product(db, product, {"status": ProductStatus.REMOVED.value})
    db.commit()
    return {"id": product_id, "deleted": True, "status": product.status}


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

    # 使用存储抽象层校验并保存图片
    storage = get_image_storage()
    url, generated_name = validate_and_save_image(storage, product_id, filename, content_type, content)

    from app.core.settings import settings as app_settings
    if app_settings.cos_enabled:
        # COS 模式下：数据库存真实 COS URL，序列化时自动转成代理路径
        stored_url = url
    else:
        # 本地模式下：拼接 base_url
        stored_url = f"{base_url}{url}"

    try:
        image = product_crud.add_product_image(db, product_id, stored_url)
        db.commit()
        db.refresh(image)
        # 返回给前端的 URL 用代理路径（COS 模式下绕过防盗链）
        if app_settings.cos_enabled:
            display_url = f"{base_url}/api/products/{product_id}/images/{image.id}/content"
        else:
            display_url = stored_url
    except IntegrityError as exc:
        db.rollback()
        storage.delete(url)
        raise DuplicateConflictError("product image already exists", {"productId": product_id}) from exc
    return {"id": image.id, "productId": product_id, "filename": generated_name, "url": display_url}


def get_product_image(db: Session, product_id: int, image_id: int):
    """获取图片记录（代理用）"""
    from app.crud.product import get_product_image as _get_image
    image = _get_image(db, product_id, image_id)
    if image is None:
        raise ResourceNotFoundError("product image not found", {"productId": product_id, "imageId": image_id})
    return image


def delete_product_image(db: Session, product_id: int, image_id: int, actor: CurrentActor) -> dict:
    product = _require_product(db, product_id)
    _require_owner(product, actor)
    image = product_crud.get_product_image(db, product_id, image_id)
    if image is None:
        raise ResourceNotFoundError("product image not found", {"productId": product_id, "imageId": image_id})
    # 从存储后端删除文件
    storage = get_image_storage()
    storage.delete(image.url)
    product_crud.delete_product_image(db, image)
    db.commit()
    return {"productId": product_id, "imageId": image_id, "deleted": True}


def list_pending_products(db: Session, page: int = 1, size: int = 20) -> dict:
    page = max(page, 1)
    size = min(max(size, 1), 100)
    items, total = product_crud.list_products(
        db,
        page,
        size,
        status=ProductStatus.PENDING.value,
    )
    return {"list": items, "page": {"page": page, "size": size, "total": total}}


def review_product(db: Session, product_id: int, result: str, reason: str | None = None) -> dict:
    product = _require_product(db, product_id, for_update=True)
    target = ProductStatus.PUBLISHED.value if result == "approved" else ProductStatus.REMOVED.value
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
