from copy import deepcopy
from datetime import datetime, timezone

from app.core.status import ProductStatus


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


_products: dict[int, dict] = {
    1001: {
        "id": 1001,
        "ownerId": 1,
        "title": "Used calculus textbook",
        "description": "Good condition, available near library.",
        "price": 35.0,
        "categoryId": 3,
        "status": ProductStatus.PUBLISHED.value,
        "images": ["https://cdn.example.com/p/1001-1.jpg"],
        "createdAt": "2026-05-14T08:10:00+00:00",
        "updatedAt": "2026-05-14T08:15:00+00:00",
        "favoriteCount": 2,
        "viewCount": 15,
    },
    1002: {
        "id": 1002,
        "ownerId": 1,
        "title": "Desk lamp",
        "description": "Adjustable brightness.",
        "price": 28.0,
        "categoryId": 4,
        "status": ProductStatus.PUBLISHED.value,
        "images": [],
        "createdAt": "2026-05-15T09:00:00+00:00",
        "updatedAt": "2026-05-15T09:00:00+00:00",
        "favoriteCount": 0,
        "viewCount": 4,
    },
}
_next_product_id = 1003
_next_image_id = 1
_images: dict[int, dict] = {}


def list_products(
    page: int,
    size: int,
    keyword: str | None = None,
    sort: str | None = None,
    category_id: int | None = None,
) -> tuple[list[dict], int]:
    items = [deepcopy(product) for product in _products.values()]

    if keyword:
        lowered = keyword.lower()
        items = [
            item
            for item in items
            if lowered in item["title"].lower() or lowered in (item.get("description") or "").lower()
        ]
    if category_id is not None:
        items = [item for item in items if item.get("categoryId") == category_id]

    if sort == "price_asc":
        items.sort(key=lambda item: item["price"])
    elif sort == "price_desc":
        items.sort(key=lambda item: item["price"], reverse=True)
    else:
        items.sort(key=lambda item: item.get("createdAt") or "", reverse=True)

    total = len(items)
    start = (page - 1) * size
    end = start + size
    return items[start:end], total


def create_product(payload: dict, owner_id: int | None = 1) -> dict:
    global _next_product_id
    product_id = _next_product_id
    _next_product_id += 1
    now = _now()
    product = {
        "id": product_id,
        "ownerId": owner_id,
        "title": payload["title"],
        "description": payload.get("description"),
        "price": float(payload["price"]),
        "categoryId": payload["categoryId"],
        "status": ProductStatus.PENDING.value,
        "images": list(payload.get("images") or []),
        "createdAt": now,
        "updatedAt": now,
        "favoriteCount": 0,
        "viewCount": 0,
    }
    _products[product_id] = product
    return deepcopy(product)


def get_product(product_id: int) -> dict | None:
    product = _products.get(product_id)
    return deepcopy(product) if product else None


def increment_view_count(product_id: int) -> dict | None:
    product = _products.get(product_id)
    if product is None:
        return None
    product["viewCount"] = int(product.get("viewCount") or 0) + 1
    product["updatedAt"] = _now()
    return deepcopy(product)


def update_product(product_id: int, changes: dict) -> dict | None:
    product = _products.get(product_id)
    if product is None:
        return None
    for key, value in changes.items():
        product[key] = value
    product["updatedAt"] = _now()
    return deepcopy(product)


def add_product_image(product_id: int, filename: str) -> dict | None:
    global _next_image_id
    product = _products.get(product_id)
    if product is None:
        return None
    image_id = _next_image_id
    _next_image_id += 1
    url = f"/static/products/{product_id}/{filename}"
    image = {"id": image_id, "productId": product_id, "filename": filename, "url": url}
    _images[image_id] = image
    product.setdefault("images", []).append(url)
    product["updatedAt"] = _now()
    return deepcopy(image)


def delete_product_image(product_id: int, image_id: int) -> bool | None:
    product = _products.get(product_id)
    if product is None:
        return None
    image = _images.get(image_id)
    if image is None or image["productId"] != product_id:
        return False
    product["images"] = [url for url in product.get("images", []) if url != image["url"]]
    product["updatedAt"] = _now()
    del _images[image_id]
    return True
