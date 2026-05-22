from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"
load_dotenv(ENV_FILE)


class Settings:
    # 微信配置
    WECHAT_APP_ID: str = os.getenv("WECHAT_APP_ID", "")
    WECHAT_APP_SECRET: str = os.getenv("WECHAT_APP_SECRET", "")
    
    # JWT配置（改为大写）
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-jwt-secret")
    JWT_EXPIRES_SECONDS: int = int(os.getenv("JWT_EXPIRES_SECONDS", "3600"))
    JWT_REFRESH_EXPIRES_SECONDS: int = int(os.getenv("JWT_REFRESH_EXPIRES_SECONDS", "604800"))
    
    # 数据库配置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@localhost:3306/campus_market")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()