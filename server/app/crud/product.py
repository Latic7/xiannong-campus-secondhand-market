from __future__ import annotations

from decimal import Decimal

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.product_image import ProductImage


def _iso(value) -> str | None:
    return value.isoformat() if value else None


def serialize_product(db: Session, product: Product) -> dict:
    images = db.scalars(
        select(ProductImage.url).where(ProductImage.product_id == product.id).order_by(ProductImage.id)
    ).all()
    return {
        "id": product.id,
        "ownerId": product.owner_id,
        "title": product.title,
        "description": product.description,
        "price": float(product.price),
        "categoryId": product.category_id,
        "status": product.status,
        "images": list(images),
        "createdAt": _iso(product.created_at),
        "updatedAt": _iso(product.updated_at),
        "favoriteCount": product.favorite_count or 0,
        "viewCount": product.view_count or 0,
    }


def list_products(
    db: Session,
    page: int,
    size: int,
    keyword: str | None = None,
    sort: str | None = None,
    category_id: int | None = None,
    status: str | None = None,
) -> tuple[list[dict], int]:
    filters = []
    if keyword:
        pattern = f"%{keyword}%"
        filters.append(or_(Product.title.ilike(pattern), Product.description.ilike(pattern)))
    if category_id is not None:
        filters.append(Product.category_id == category_id)
    if status is not None:
        filters.append(Product.status == status)

    total = db.scalar(select(func.count(Product.id)).where(*filters)) or 0
    statement = select(Product).where(*filters)
    if sort == "price_asc":
        statement = statement.order_by(Product.price.asc(), Product.id.asc())
    elif sort == "price_desc":
        statement = statement.order_by(Product.price.desc(), Product.id.asc())
    else:
        statement = statement.order_by(Product.created_at.desc(), Product.id.desc())
    products = db.scalars(statement.offset((page - 1) * size).limit(size)).all()
    return [serialize_product(db, product) for product in products], total


def create_product(db: Session, payload: dict, owner_id: int) -> Product:
    image_urls = payload.pop("images", [])
    product = Product(
        owner_id=owner_id,
        title=payload["title"],
        description=payload.get("description"),
        price=Decimal(str(payload["price"])),
        category_id=payload["categoryId"],
        status="pending",
    )
    db.add(product)
    db.flush()
    for url in image_urls:
        db.add(ProductImage(product_id=product.id, url=url))
    db.flush()
    return product


def get_product(db: Session, product_id: int, *, for_update: bool = False) -> Product | None:
    statement = select(Product).where(Product.id == product_id)
    if for_update:
        statement = statement.with_for_update()
    return db.scalar(statement)


def update_product(db: Session, product: Product, changes: dict) -> Product:
    mapping = {"categoryId": "category_id"}
    for key, value in changes.items():
        setattr(product, mapping.get(key, key), Decimal(str(value)) if key == "price" else value)
    db.flush()
    return product


def increment_view_count(db: Session, product: Product) -> Product:
    product.view_count = (product.view_count or 0) + 1
    db.flush()
    return product


def add_product_image(db: Session, product_id: int, url: str) -> ProductImage:
    image = ProductImage(product_id=product_id, url=url)
    db.add(image)
    db.flush()
    return image


def get_product_image(db: Session, product_id: int, image_id: int) -> ProductImage | None:
    return db.scalar(
        select(ProductImage).where(ProductImage.id == image_id, ProductImage.product_id == product_id)
    )


def delete_product_image(db: Session, image: ProductImage) -> None:
    db.delete(image)
    db.flush()
