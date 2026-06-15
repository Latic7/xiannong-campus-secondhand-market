from fastapi import APIRouter, Depends, File, Query, Request, UploadFile
from sqlalchemy.orm import Session

from app.api.deps.auth import CurrentActor, get_current_actor
from app.core.database import get_db
from app.core.exceptions import ResourceNotFoundError
from app.core.response import api_ok
from app.schemas.common import ProductCreateRequest, ProductUpdateRequest
from app.services import product_service

router = APIRouter(prefix="/api/products", tags=["Product"])


@router.get("")
def list_products(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    keyword: str | None = None,
    sort: str | None = None,
    categoryId: int | None = None,
    ownerId: int | None = None,
    db: Session = Depends(get_db),
) -> dict:
    return api_ok(product_service.list_products(db, page, size, keyword, sort, categoryId, owner_id=ownerId))


@router.post("")
def create_product(
    payload: ProductCreateRequest,
    db: Session = Depends(get_db),
    actor: CurrentActor = Depends(get_current_actor),
) -> dict:
    return api_ok(product_service.create_product(db, payload, actor))


@router.get("/{product_id}")
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
) -> dict:
    product = product_service.get_product(db, product_id)
    if product is None:
        raise ResourceNotFoundError("product not found", {"productId": product_id})
    return api_ok(product)


@router.put("/{product_id}")
def update_product(
    product_id: int,
    payload: ProductUpdateRequest,
    db: Session = Depends(get_db),
    actor: CurrentActor = Depends(get_current_actor),
) -> dict:
    return api_ok(product_service.update_product(db, product_id, payload, actor))


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    actor: CurrentActor = Depends(get_current_actor),
) -> dict:
    return api_ok(product_service.remove_product(db, product_id, actor))


@router.post("/{product_id}/images")
async def upload_product_image(
    product_id: int,
    file: UploadFile = File(...),
    request: Request = None,
    db: Session = Depends(get_db),
    actor: CurrentActor = Depends(get_current_actor),
) -> dict:
    content = await file.read()
    base_url = str(request.base_url).rstrip("/") if request else "http://localhost:8000"
    result = product_service.upload_product_image(
        db, product_id, file.filename or "upload.bin", file.content_type, content, actor, base_url
    )
    return api_ok(result)


@router.delete("/{product_id}/images/{image_id}")
def delete_product_image(
    product_id: int,
    image_id: int,
    db: Session = Depends(get_db),
    actor: CurrentActor = Depends(get_current_actor),
) -> dict:
    return api_ok(product_service.delete_product_image(db, product_id, image_id, actor))
