"""
图片存储 - 本地文件系统存储

图片保存在 server/static/products/{product_id}/ 目录下，
通过 FastAPI 挂载的 /static 路由访问。
"""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from app.core.exceptions import InvalidRequestError
from app.core.settings import settings

# ── 图片类型白名单 ────────────────────────────────────
ALLOWED_IMAGE_TYPES: dict[str, str] = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
ALLOWED_IMAGE_EXTENSIONS: set[str] = {".jpg", ".jpeg", ".png", ".webp"}
MAX_IMAGE_SIZE: int = 5 * 1024 * 1024  # 5 MiB


def save_product_image(
    product_id: int,
    filename: str,
    content_type: str | None,
    content: bytes,
) -> tuple[str, str]:
    """
    校验图片并保存到本地文件系统。
    返回 (url相对路径, generated_name)。
    """
    suffix = Path(filename).suffix.lower()
    if not filename or suffix not in ALLOWED_IMAGE_EXTENSIONS or content_type not in ALLOWED_IMAGE_TYPES:
        raise InvalidRequestError("unsupported image type")
    if not content:
        raise InvalidRequestError("image file is empty")
    if len(content) > MAX_IMAGE_SIZE:
        raise InvalidRequestError("image file exceeds 5 MiB limit")

    generated_name = f"{uuid4().hex}{ALLOWED_IMAGE_TYPES[content_type]}"
    product_dir = str(product_id)

    static_root = Path(settings.static_dir).resolve()
    products_root = (static_root / "products").resolve()
    file_dir = (products_root / product_dir).resolve()

    try:
        file_dir.relative_to(products_root)
    except ValueError as exc:
        raise InvalidRequestError("invalid image path") from exc

    file_dir.mkdir(parents=True, exist_ok=True)
    (file_dir / generated_name).write_bytes(content)

    url = f"/static/products/{product_dir}/{generated_name}"
    return url, generated_name


def delete_product_image_file(url: str) -> None:
    """根据 URL 删除本地图片文件"""
    static_root = Path(settings.static_dir).resolve()
    file_path = (static_root / url.lstrip("/")).resolve()
    try:
        file_path.relative_to(static_root)
    except ValueError:
        return
    file_path.unlink(missing_ok=True)
