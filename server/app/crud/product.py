from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import func, select, delete
from sqlalchemy.orm import Session

from app.core.status import ProductStatus
from app.db.session import SessionLocal
from app.models.product import Product
from app.models.product_image import ProductImage


# ── 辅助函数 ──────────────────────────────────


def _product_to_dict(product: Product, images: list[str] | None = None) -> dict:
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


def list_products(
    page: int,
    size: int,
    keyword: str | None = None,
    sort: str | None = None,
    category_id: int | None = None,
) -> tuple[list[dict], int]:
    with SessionLocal() as db:
        stmt = select(Product)

        if keyword:
            kw = f"%{keyword}%"
            stmt = stmt.where(
                Product.title.ilike(kw) | Product.description.ilike(kw)
            )
        if category_id is not None:
            stmt = stmt.where(Product.category_id == category_id)

        total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0

        if sort == "price_asc":
            stmt = stmt.order_by(Product.price.asc())
        elif sort == "price_desc":
            stmt = stmt.order_by(Product.price.desc())
        else:
            stmt = stmt.order_by(Product.created_at.desc())

        stmt = stmt.offset((page - 1) * size).limit(size)
        rows = db.execute(stmt).scalars().all()

        items = []
        for product in rows:
            images = _get_images_for_product(db, product.id)
            items.append(_product_to_dict(product, images))

        return items, total


def create_product(payload: dict, owner_id: int | None = 1) -> dict:
    with SessionLocal() as db:
        product = Product(
            owner_id=owner_id,
            title=payload["title"],
            description=payload.get("description"),
            price=Decimal(str(payload["price"])),
            category_id=payload.get("categoryId"),
            status=ProductStatus.PENDING.value,
        )
        db.add(product)
        db.commit()
        db.refresh(product)

        # 如果创建时传入 images URL，也一并写入
        initial_images = payload.get("images") or []
        for url in initial_images:
            db.add(ProductImage(
                product_id=product.id,
                url=url,
            ))
        if initial_images:
            db.commit()

        images = _get_images_for_product(db, product.id)
        return _product_to_dict(product, images)


def get_product(product_id: int) -> dict | None:
    with SessionLocal() as db:
        product = db.get(Product, product_id)
        if product is None:
            return None
        images = _get_images_for_product(db, product_id)
        return _product_to_dict(product, images)


def increment_view_count(product_id: int) -> dict | None:
    with SessionLocal() as db:
        product = db.get(Product, product_id)
        if product is None:
            return None
        product.view_count = (product.view_count or 0) + 1
        product.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(product)
        images = _get_images_for_product(db, product_id)
        return _product_to_dict(product, images)


def update_product(product_id: int, changes: dict) -> dict | None:
    """更新商品字段。changes 的 key 为 camelCase。"""
    with SessionLocal() as db:
        product = db.get(Product, product_id)
        if product is None:
            return None

        # camelCase → snake_case 映射
        field_map = {
            "title": "title",
            "price": "price",
            "categoryId": "category_id",
            "description": "description",
            "status": "status",
            "images": "_images",  # 单独处理
        }

        for camel_key, value in changes.items():
            if camel_key == "images" and value is not None:
                # 先删除旧图片记录，再插入新 URL
                db.execute(
                    delete(ProductImage).where(ProductImage.product_id == product_id)
                )
                for url in value:
                    db.add(ProductImage(
                        product_id=product_id,
                        url=url,
                    ))
            elif camel_key == "price" and value is not None:
                product.price = Decimal(str(value))
            elif camel_key in field_map and value is not None:
                setattr(product, field_map[camel_key], value)

        product.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(product)
        images = _get_images_for_product(db, product_id)
        return _product_to_dict(product, images)


def add_product_image(product_id: int, url: str) -> dict | None:
    with SessionLocal() as db:
        product = db.get(Product, product_id)
        if product is None:
            return None

        image = ProductImage(
            product_id=product_id,
            url=url,
        )
        db.add(image)
        db.commit()
        db.refresh(image)

        product.updated_at = datetime.now(timezone.utc)
        db.commit()

        return _image_to_dict(image)


def get_image(image_id: int) -> dict | None:
    with SessionLocal() as db:
        image = db.get(ProductImage, image_id)
        if image is None:
            return None
        return _image_to_dict(image)


def list_product_images(product_id: int) -> list[dict]:
    with SessionLocal() as db:
        rows = db.execute(
            select(ProductImage).where(ProductImage.product_id == product_id)
        ).scalars().all()
        return [_image_to_dict(img) for img in rows]


def delete_product_image(product_id: int, image_id: int) -> bool | None:
    with SessionLocal() as db:
        product = db.get(Product, product_id)
        if product is None:
            return None

        image = db.get(ProductImage, image_id)
        if image is None or image.product_id != product_id:
            return False

        db.delete(image)
        product.updated_at = datetime.now(timezone.utc)
        db.commit()
        return True
