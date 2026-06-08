from app.core.exceptions import ResourceNotFoundError, StateConflictError
from app.core.status import ProductStatus
from app.crud import product as product_crud
from app.schemas.products import ProductCreateRequest, ProductUpdateRequest


def list_products(
    page: int = 1,
    size: int = 20,
    keyword: str | None = None,
    sort: str | None = None,
    category_id: int | None = None,
) -> dict:
    page = max(page, 1)
    size = min(max(size, 1), 100)
    items, total = product_crud.list_products(page, size, keyword, sort, category_id)
    return {
        "list": items,
        "page": {"page": page, "size": size, "total": total},
        "filters": {"keyword": keyword, "sort": sort, "categoryId": category_id},
    }


def create_product(payload: ProductCreateRequest) -> dict:
    return product_crud.create_product(payload.model_dump())


def get_product(product_id: int) -> dict:
    product = product_crud.increment_view_count(product_id)
    if product is None:
        raise ResourceNotFoundError("product not found", {"productId": product_id})
    return product


def update_product(product_id: int, payload: ProductUpdateRequest) -> dict:
    changes = payload.model_dump(exclude_none=True)
    if not changes:
        product = product_crud.get_product(product_id)
        if product is None:
            raise ResourceNotFoundError("product not found", {"productId": product_id})
        return product

    product = product_crud.get_product(product_id)
    if product is None:
        raise ResourceNotFoundError("product not found", {"productId": product_id})
    if product["status"] == ProductStatus.SOLD.value and any(key in changes for key in ("price", "status")):
        raise StateConflictError("sold products cannot change price or status", {"productId": product_id})

    updated = product_crud.update_product(product_id, changes)
    if updated is None:
        raise ResourceNotFoundError("product not found", {"productId": product_id})
    return updated


def remove_product(product_id: int) -> dict:
    product = product_crud.update_product(product_id, {"status": ProductStatus.REMOVED.value})
    if product is None:
        raise ResourceNotFoundError("product not found", {"productId": product_id})
    return {"id": product_id, "deleted": True, "status": product["status"]}


def upload_product_image(product_id: int, filename: str) -> dict:
    image = product_crud.add_product_image(product_id, filename)
    if image is None:
        raise ResourceNotFoundError("product not found", {"productId": product_id})
    return image


def delete_product_image(product_id: int, image_id: int) -> dict:
    deleted = product_crud.delete_product_image(product_id, image_id)
    if deleted is None:
        raise ResourceNotFoundError("product not found", {"productId": product_id})
    if not deleted:
        raise ResourceNotFoundError("product image not found", {"productId": product_id, "imageId": image_id})
    return {"productId": product_id, "imageId": image_id, "deleted": True}
