"""
文件处理工具模块
负责图片上传的校验、本地存储、URL 生成。
设计为可替换后端，方便后续迁移到腾讯云 COS / 微信云托管。
"""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import UploadFile

from app.core.settings import settings


# ── 可允许的文件扩展名 ─────────────────────────
ALLOWED_EXTENSIONS = settings.allowed_extensions

# ── 最大文件大小（字节）─────────────────────────
MAX_FILE_SIZE = settings.max_upload_size


class FileValidationError(ValueError):
    """文件校验失败时抛出的异常。"""
    pass


def validate_image(file: UploadFile) -> str:
    """
    校验上传的文件是否为合法的图片。
    
    返回：标准化后的小写扩展名（如 '.jpg'）
    抛出：FileValidationError
    """
    # 1. 读取文件扩展名
    filename = file.filename or ""
    suffix = Path(filename).suffix.lower()

    if not suffix:
        raise FileValidationError("无法识别文件类型")

    if suffix not in ALLOWED_EXTENSIONS:
        raise FileValidationError(
            f"不支持的图片格式 '{suffix}'，允许的格式：{', '.join(ALLOWED_EXTENSIONS)}"
        )

    return suffix


async def read_and_check_size(file: UploadFile) -> bytes:
    """
    读取文件内容并检查大小是否超出限制。
    
    返回：文件字节内容
    抛出：FileValidationError（文件过大时）
    """
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise FileValidationError(
            f"图片大小超过限制（最大 {MAX_FILE_SIZE // (1024 * 1024)} MB）"
        )
    return content


def generate_filename(extension: str) -> str:
    """生成 UUID 文件名，如 'a1b2c3d4-e5f6-7890-abcd-ef1234567890.jpg'"""
    return f"{uuid.uuid4().hex}{extension}"


def save_file(content: bytes, filename: str) -> Path:
    """
    将文件保存到本地 media 目录。
    
    返回：文件的完整 Path 对象
    """
    media_dir = Path(settings.media_dir)
    media_dir.mkdir(parents=True, exist_ok=True)

    file_path = media_dir / filename
    file_path.write_bytes(content)
    return file_path


def get_media_url(filename: str) -> str:
    """
    获取文件的访问 URL。
    
    当前（本地开发）：返回 FastAPI 静态文件路径
    未来（微信云托管）：应返回 cloud://xxx.png 格式的 URL
    """
    return f"/media/{filename}"


def delete_file_from_disk(filepath: str | Path) -> None:
    """
    从磁盘删除文件。
    
    ⚠️ 当前为空实现——删除文件操作有风险，后续确认无误后再启用。
    TODO: 接入腾讯云 COS 后，在此处调用 COS 删除接口。
    """
    # path = Path(filepath)
    # if path.exists():
    #     path.unlink()
    pass
