"""
图片存储抽象层

支持两种存储后端：
  - local: 本地文件系统（默认，开发环境使用）
  - cos:   腾讯云对象存储 COS（生产环境使用）

通过 settings.cos_enabled 切换后端，无需修改业务代码。
"""

from __future__ import annotations

import os
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

    @abstractmethod
    def read(self, url: str) -> bytes:
        """根据 URL 读取图片的原始字节"""
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

    def read(self, url: str) -> bytes:
        """从本地文件系统读取图片"""
        static_root = Path(settings.static_dir).resolve()
        file_path = (static_root / url.lstrip("/")).resolve()
        try:
            file_path.relative_to(static_root)
        except ValueError:
            raise InvalidRequestError("invalid image path")
        return file_path.read_bytes()


class CosImageStorage(ImageStorage):
    """腾讯云对象存储 COS

    支持两种凭证来源（按优先级）：
    1. 云托管运行时自动注入的 TENCENTCLOUD_* 环境变量（无需手动配密钥）
    2. settings.py 中显式配置的 COS_SECRET_ID / COS_SECRET_KEY
    """

    def __init__(self) -> None:
        from qcloud_cos import CosConfig, CosS3Client

        self._bucket = settings.cos_bucket
        self._base_url = settings.cos_base_url.rstrip("/") if settings.cos_base_url else ""

        # 尝试从云托管环境变量读取凭证（优先级高）
        env_secret_id = os.environ.get("TENCENTCLOUD_SECRETID") or os.environ.get("COS_SECRET_ID")
        env_secret_key = os.environ.get("TENCENTCLOUD_SECRETKEY") or os.environ.get("COS_SECRET_KEY")
        env_token = os.environ.get("TENCENTCLOUD_SESSIONTOKEN")

        secret_id = env_secret_id or settings.cos_secret_id
        secret_key = env_secret_key or settings.cos_secret_key

        if not secret_id or not secret_key:
            # 输出调试信息到云日志
            _dbg = (
                f"env[COS_SECRET_ID]={'SET' if os.environ.get('COS_SECRET_ID') else 'EMPTY'}, "
                f"env[COS_SECRET_KEY]={'SET' if os.environ.get('COS_SECRET_KEY') else 'EMPTY'}, "
                f"env[TENCENTCLOUD_SECRETID]={'SET' if os.environ.get('TENCENTCLOUD_SECRETID') else 'EMPTY'}, "
                f"settings.cos_secret_id={'SET' if settings.cos_secret_id else 'EMPTY'}"
            )
            raise RuntimeError(
                f"COS enabled but no credentials found. Debug: {_dbg}. "
                f"Set COS_SECRET_ID/COS_SECRET_KEY in env, "
                f"or deploy on WeChat Cloud Hosting with built-in storage."
            )

        config = CosConfig(
            Region=settings.cos_region,
            SecretId=secret_id,
            SecretKey=secret_key,
            Token=env_token,  # 云托管临时凭证需要 Token
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
        key = self._extract_key(url)
        if not key:
            return
        try:
            self._client.delete_object(Bucket=self._bucket, Key=key)
        except Exception:
            pass  # 删除失败不影响主流程

    def read(self, url: str) -> bytes:
        """从 COS 读取图片原始字节"""
        key = self._extract_key(url)
        if not key:
            raise InvalidRequestError("invalid image url")
        response = self._client.get_object(Bucket=self._bucket, Key=key)
        return response["Body"].read()

    def _extract_key(self, url: str) -> str:
        """从 URL 中提取 COS object key"""
        if ".myqcloud.com/" in url:
            return url.split(".myqcloud.com/")[-1]
        return url.lstrip("/")


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
