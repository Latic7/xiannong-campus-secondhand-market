from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import func, select, delete, update
from sqlalchemy.orm import Session

from app.core.status import ProductStatus
from app.models.product import Product
from app.models.product_image import ProductImage
from app.models.user import User


# ── 辅助函数 ──────────────────────────────────


def _owner_to_seller_dict(owner: User | None) -> dict:
    """将 User ORM 对象转为前端期望的 seller 字典。"""
    if owner is None:
        return {
            "id": 0,
            "nickname": "未知用户",
            "avatar": "",
            "reputation": 0,
        }
    return {
        "id": owner.id,
        "nickname": owner.nickname or "未知用户",
        "avatar": owner.avatar or "",
        "reputation": owner.score if owner.score is not None else 100,
    }


def _product_to_dict(product: Product, images: list[str] | None = None, seller: dict | None = None) -> dict:
    """将 ORM Product 对象转为前端期望的 camelCase 字典。"""
    return {
        "id": product.id,
        "ownerId": product.owner_id,
        "title": product.title,
        "description": product.description or "",
        "price": float(product.price) if isinstance(product.price, Decimal) else float(product.price or 0),
        "categoryId": product.category_id,
        "status": product.status or ProductStatus.PENDING.value,
        "images": images or [],
        "createdAt": product.created_at.isoformat() if product.created_at else "",
        "updatedAt": product.updated_at.isoformat() if product.updated_at else "",
        "favoriteCount": product.favorite_count or 0,
        "viewCount": product.view_count or 0,
        "seller": seller or _owner_to_seller_dict(None),
    }


def _get_images_for_product(db: Session, product_id: int) -> list[str]:
    """查询某商品的所有图片 URL 列表。"""
    rows = db.execute(
        select(ProductImage.url).where(ProductImage.product_id == product_id)
    ).all()
    return [row[0] for row in rows]


def _image_to_dict(image: ProductImage) -> dict:
    return {
        "id": image.id,
        "productId": image.product_id,
        "url": image.url,
    }


# ── 公开 CRUD 方法 ────────────────────────────


def get_product(db: Session, product_id: int, *, for_update: bool = False) -> Product | None:
    """返回 ORM Product 对象（非 dict），供 service 层使用。"""
    statement = select(Product).where(Product.id == product_id)
    if for_update:
        statement = statement.with_for_update()
    return db.scalar(statement)


def serialize_product(db: Session, product: Product) -> dict:
    """将 ORM Product 转为前端期望的 camelCase 字典（含 images 和 seller）。"""
    images = _get_images_for_product(db, product.id)
    seller = None
    if product.owner_id:
        owner = db.get(User, product.owner_id)
        seller = _owner_to_seller_dict(owner)
    return _product_to_dict(product, images, seller)


def list_products(
    db: Session,
    page: int,
    size: int,
    keyword: str | None = None,
    sort: str | None = None,
    category_id: int | None = None,
    status: str | list[str] | None = None,
    owner_id: int | None = None,
) -> tuple[list[dict], int]:
    stmt = select(Product)

    if keyword:
        kw = f"%{keyword}%"
        stmt = stmt.where(
            Product.title.ilike(kw) | Product.description.ilike(kw)
        )
    if category_id is not None:
        stmt = stmt.where(Product.category_id == category_id)
    if status is not None:
        if isinstance(status, list):
            stmt = stmt.where(Product.status.in_(status))
        else:
            stmt = stmt.where(Product.status == status)
    if owner_id is not None:
        stmt = stmt.where(Product.owner_id == owner_id)

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0

    if sort == "price_asc":
        stmt = stmt.order_by(Product.price.asc())
    elif sort == "price_desc":
        stmt = stmt.order_by(Product.price.desc())
    else:
        stmt = stmt.order_by(Product.created_at.desc())

    stmt = stmt.offset((page - 1) * size).limit(size)
    rows = db.execute(stmt).scalars().all()

    return [serialize_product(db, p) for p in rows], total


def create_product(db: Session, payload: dict, owner_id: int | None = 1) -> Product:
    """返回 ORM Product 对象，由调用方负责 commit + refresh。"""
    product = Product(
        owner_id=owner_id,
        title=payload["title"],
        description=payload.get("description"),
        price=Decimal(str(payload["price"])),
        category_id=payload.get("categoryId"),
        status=ProductStatus.PENDING.value,
    )
    db.add(product)
    return product


def increment_view_count(db: Session, product: Product) -> None:
    product.view_count = (product.view_count or 0) + 1
    product.updated_at = datetime.now(timezone.utc)


def update_product(db: Session, product: Product, changes: dict) -> None:
    """用 changes dict（snake_case key）直接更新 ORM 对象。"""
    for key, value in changes.items():
        if key == "price" and value is not None:
            setattr(product, "price", Decimal(str(value)))
        elif value is not None:
            setattr(product, key, value)
    product.updated_at = datetime.now(timezone.utc)


def add_product_image(db: Session, product_id: int, url: str) -> ProductImage:
    """返回 ORM ProductImage 对象，由调用方负责 commit + refresh。"""
    image = ProductImage(product_id=product_id, url=url)
    db.add(image)
    return image


def get_product_image(db: Session, product_id: int, image_id: int) -> ProductImage | None:
    return db.execute(
        select(ProductImage).where(
            ProductImage.id == image_id,
            ProductImage.product_id == product_id,
        )
    ).scalar_one_or_none()


def delete_product_image(db: Session, image: ProductImage) -> None:
    db.delete(image)


def update_product_image_url(db: Session, image_id: int, url: str) -> None:
    """更新图片 URL"""
    db.execute(
        update(ProductImage).where(ProductImage.id == image_id).values(url=url)
    )
