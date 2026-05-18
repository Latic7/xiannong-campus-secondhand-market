from fastapi import APIRouter, File, UploadFile

from app.core.response import api_ok
from app.schemas.common import ProductCreateRequest, ProductUpdateRequest

router = APIRouter(prefix="/api/products", tags=["Product"])


@router.get("")
def list_products(
    page: int = 1,
    size: int = 20,
    keyword: str | None = None,
    sort: str | None = None,
    categoryId: int | None = None,
) -> dict:
    return api_ok(
        {
            "list": [],
            "page": {"page": page, "size": size, "total": 0},
            "filters": {"keyword": keyword, "sort": sort, "categoryId": categoryId},
        }
    )


@router.post("")
def create_product(payload: ProductCreateRequest) -> dict:
    return api_ok({"id": 1001, **payload.model_dump(), "status": "pending"})


@router.get("/{product_id}")
def get_product(product_id: int) -> dict:
    return api_ok({"id": product_id, "title": "Draft Product", "price": 0, "status": "published"})


@router.put("/{product_id}")
def update_product(product_id: int, payload: ProductUpdateRequest) -> dict:
    return api_ok({"id": product_id, "updated": payload.model_dump(exclude_none=True)})


@router.delete("/{product_id}")
def delete_product(product_id: int) -> dict:
    return api_ok({"id": product_id, "deleted": True})


@router.post("/{product_id}/images")
def upload_product_image(product_id: int, file: UploadFile = File(...)) -> dict:
    return api_ok({"productId": product_id, "filename": file.filename})


@router.delete("/{product_id}/images/{image_id}")
def delete_product_image(product_id: int, image_id: int) -> dict:
    return api_ok({"productId": product_id, "imageId": image_id, "deleted": True})
