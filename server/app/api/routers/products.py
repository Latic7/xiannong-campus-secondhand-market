from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.api.deps.auth import CurrentActor, get_current_actor
from app.core.response import api_ok
from app.db.session import get_db
from app.schemas.products import ProductCreateRequest, ProductUpdateRequest
from app.services import product_service

router = APIRouter(prefix="/api/products", tags=["Product"])


@router.get("")
def list_products(
    page: int = 1,
    size: int = 20,
    keyword: str | None = None,
    sort: str | None = None,
    categoryId: int | None = None,
    db: Session = Depends(get_db),
) -> dict:
    return api_ok(product_service.list_products(db, page, size, keyword, sort, categoryId))


@router.post("")
def create_product(
    payload: ProductCreateRequest,
    db: Session = Depends(get_db),
    actor: CurrentActor = Depends(get_current_actor),
) -> dict:
    return api_ok(product_service.create_product(db, payload, actor))


@router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)) -> dict:
    return api_ok(product_service.get_product(db, product_id))


@router.put("/{product_id}")
def update_product(
    product_id: int,
    payload: ProductUpdateRequest,
    db: Session = Depends(get_db),
    actor: CurrentActor = Depends(get_current_actor),
) -> dict:
    product_service.update_product(db, product_id, payload, actor)
    return api_ok({"updated": True, "productId": product_id})


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    actor: CurrentActor = Depends(get_current_actor),
) -> dict:
    return api_ok(product_service.remove_product(db, product_id, actor))


@router.post("/{product_id}/images")
def upload_product_image(
    product_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    actor: CurrentActor = Depends(get_current_actor),
) -> dict:
    image = product_service.upload_product_image(
        db, product_id, file.filename or "", file.content_type, file.file.read(), actor
    )
    return api_ok({"productId": product_id, "filename": image["filename"], "imageId": image["id"], "url": image["url"]})


@router.delete("/{product_id}/images/{image_id}")
def delete_product_image(
    product_id: int,
    image_id: int,
    db: Session = Depends(get_db),
    actor: CurrentActor = Depends(get_current_actor),
) -> dict:
    return api_ok(product_service.delete_product_image(db, product_id, image_id, actor))
