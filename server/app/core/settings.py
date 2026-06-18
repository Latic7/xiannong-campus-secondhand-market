from pathlib import Path
import os
from dotenv import load_dotenv
from typing import List

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"
load_dotenv(ENV_FILE)


class Settings:
    wechat_app_id: str = os.getenv("WECHAT_APP_ID", "")
    wechat_app_secret: str = os.getenv("WECHAT_APP_SECRET", "")
    jwt_secret: str = os.getenv("JWT_SECRET", "dev-jwt-secret")
    jwt_expires_seconds: int = int(os.getenv("JWT_EXPIRES_SECONDS", "3600"))
    jwt_refresh_expires_seconds: int = int(
        os.getenv("JWT_REFRESH_EXPIRES_SECONDS", "604800")
    )
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./campus_market.db")
    
    # 管理员创建密码配置
    # 支持多个密码，用逗号分隔，例如: "admin123,secret456,superkey"
    admin_creation_secrets_str: str = os.getenv("ADMIN_CREATION_SECRETS", "your_admin_secret_key_123")
    admin_creation_secrets: List[str] = [s.strip() for s in admin_creation_secrets_str.split(",")]
    
    # 文件上传配置
    media_dir: str = str(BASE_DIR / "media")
    static_dir: str = str(BASE_DIR / "static")
    max_upload_size: int = 5 * 1024 * 1024  # 5 MB
    allowed_extensions: tuple = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp")

    # 调试模式
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"

    # 兼容旧代码中使用的大写配置名
    MEDIA_DIR: str = media_dir
    MAX_UPLOAD_SIZE: int = max_upload_size
    ALLOWED_EXTENSIONS: tuple = allowed_extensions

    WECHAT_APP_ID: str = wechat_app_id
    WECHAT_APP_SECRET: str = wechat_app_secret
    JWT_SECRET: str = jwt_secret
    JWT_EXPIRES_SECONDS: int = jwt_expires_seconds
    JWT_REFRESH_EXPIRES_SECONDS: int = jwt_refresh_expires_seconds
    DATABASE_URL: str = database_url
    ADMIN_CREATION_SECRETS: List[str] = admin_creation_secrets
    DEBUG: bool = debug


settings = Settings()