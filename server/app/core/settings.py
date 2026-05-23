from pathlib import Path
import os
from dotenv import load_dotenv

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

settings = Settings()