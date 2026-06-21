"""
图片存储抽象层

支持两种存储后端：
  - local: 本地文件系统（默认，开发环境使用）
  - cos:   腾讯云对象存储 COS（生产环境使用）

通过 settings.cos_enabled 切换后端，无需修改业务代码。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
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


class ImageStorage(ABC):
    """图片存储抽象基类"""

    @abstractmethod
    def save(self, product_id: int, content_type: str, content: bytes) -> str:
        """保存图片并返回可公开访问的 URL"""
        ...

    @abstractmethod
    def delete(self, url: str) -> None:
        """根据 URL 删除已上传的图片"""
        ...


class LocalImageStorage(ImageStorage):
    """本地文件系统存储"""

    def save(self, product_id: int, content_type: str, content: bytes) -> str:
        suffix = ALLOWED_IMAGE_TYPES[content_type]
        generated_name = f"{uuid4().hex}{suffix}"
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

        return f"/static/products/{product_dir}/{generated_name}"

    def delete(self, url: str) -> None:
        """删除本地图片文件"""
        # url 形如 /static/products/{product_id}/{filename}
        static_root = Path(settings.static_dir).resolve()
        file_path = (static_root / url.lstrip("/")).resolve()
        try:
            file_path.relative_to(static_root)
        except ValueError:
            return  # 安全保护：不允许删除 static 目录之外的文件
        file_path.unlink(missing_ok=True)


class CosImageStorage(ImageStorage):
    """腾讯云对象存储 COS"""

    def __init__(self) -> None:
        from qcloud_cos import CosConfig, CosS3Client

        self._bucket = settings.cos_bucket
        self._base_url = settings.cos_base_url.rstrip("/")
        config = CosConfig(
            Region=settings.cos_region,
            SecretId=settings.cos_secret_id,
            SecretKey=settings.cos_secret_key,
        )
        self._client = CosS3Client(config)

    def save(self, product_id: int, content_type: str, content: bytes) -> str:
        suffix = ALLOWED_IMAGE_TYPES[content_type]
        generated_name = f"{uuid4().hex}{suffix}"
        key = f"products/{product_id}/{generated_name}"

        self._client.put_object(
            Bucket=self._bucket,
            Body=content,
            Key=key,
            ContentType=content_type,
        )

        if self._base_url:
            return f"{self._base_url}/{key}"
        # 如果没有自定义域名，使用 COS 默认域名
        return f"https://{self._bucket}.cos.{settings.cos_region}.myqcloud.com/{key}"

    def delete(self, url: str) -> None:
        """从 COS 删除图片"""
        # 从 URL 中提取 object key
        # 例如: https://bucket.cos.region.myqcloud.com/products/1001/abc.jpg
        # 或    /products/1001/abc.jpg
        key = url.split(".myqcloud.com/")[-1] if ".myqcloud.com/" in url else url.lstrip("/")
        if not key.startswith("products/"):
            return  # 安全保护
        try:
            self._client.delete_object(Bucket=self._bucket, Key=key)
        except Exception:
            pass  # 删除失败不影响主流程


def get_image_storage() -> ImageStorage:
    """根据配置返回对应的存储后端实例"""
    if settings.cos_enabled:
        return CosImageStorage()
    return LocalImageStorage()


def validate_and_save_image(
    storage: ImageStorage,
    product_id: int,
    filename: str,
    content_type: str | None,
    content: bytes,
) -> tuple[str, str]:
    """
    校验图片并保存，返回 (url, generated_name)

    校验规则：
    - 文件扩展名必须在 ALLOWED_IMAGE_EXTENSIONS 内
    - MIME 类型必须在 ALLOWED_IMAGE_TYPES 内
    - 文件不能为空
    - 文件大小不能超过 MAX_IMAGE_SIZE
    """
    suffix = Path(filename).suffix.lower()
    if not filename or suffix not in ALLOWED_IMAGE_EXTENSIONS or content_type not in ALLOWED_IMAGE_TYPES:
        raise InvalidRequestError("unsupported image type")
    if not content:
        raise InvalidRequestError("image file is empty")
    if len(content) > MAX_IMAGE_SIZE:
        raise InvalidRequestError("image file exceeds 5 MiB limit")

    url = storage.save(product_id, content_type, content)
    generated_name = url.rstrip("/").split("/")[-1]
    return url, generated_name
