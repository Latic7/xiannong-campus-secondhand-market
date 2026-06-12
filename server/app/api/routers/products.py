from fastapi import APIRouter, File, UploadFile

from app.core.exceptions import ResourceNotFoundError
from app.core.response import api_ok
from app.schemas.common import ProductCreateRequest, ProductUpdateRequest
from app.services import product_service

router = APIRouter(prefix="/api/products", tags=["Product"])


@router.get("")
def list_products(
    page: int = 1,
    size: int = 20,
    keyword: str | None = None,
    sort: str | None = None,
    categoryId: int | None = None,
) -> dict:
    return api_ok(product_service.list_products(page, size, keyword, sort, categoryId))


@router.post("")
def create_product(payload: ProductCreateRequest) -> dict:
    return api_ok(product_service.create_product(payload))


@router.get("/{product_id}")
def get_product(product_id: int) -> dict:
    product = product_service.get_product(product_id)
    if product is None:
        raise ResourceNotFoundError("product not found", {"productId": product_id})
    return api_ok(product)


@router.put("/{product_id}")
def update_product(product_id: int, payload: ProductUpdateRequest) -> dict:
    product_service.update_product(product_id, payload)
    return api_ok({"updated": True, "productId": product_id})


@router.delete("/{product_id}")
def delete_product(product_id: int) -> dict:
    return api_ok(product_service.remove_product(product_id))


@router.post("/{product_id}/images")
def upload_product_image(product_id: int, file: UploadFile = File(...)) -> dict:
    image = product_service.upload_product_image(product_id, file.filename or "upload.bin")
    return api_ok({"productId": product_id, "filename": image["filename"], "imageId": image["id"], "url": image["url"]})


@router.delete("/{product_id}/images/{image_id}")
def delete_product_image(product_id: int, image_id: int) -> dict:
    return api_ok(product_service.delete_product_image(product_id, image_id))
