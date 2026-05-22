"""User ORM model placeholder."""
from sqlalchemy import Column, BigInteger, String, Integer, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func

from app.core.database import Base
from app.core.status import UserStatus

class User(Base):
    __tablename__ = "users"
    
    id = Column(BigInteger, primary_key=True)
    openid = Column(String(64), unique=True, nullable=True)
    nickname = Column(String(64), nullable=False)
    avatar = Column(String(255), nullable=False, default="")
    score = Column(Integer, nullable=False, default=100)
    status = Column(SQLEnum(UserStatus), nullable=False, default=UserStatus.ACTIVE)
    college = Column(String(128), nullable=True)
    contact = Column(String(64), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())