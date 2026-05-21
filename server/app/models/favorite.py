from sqlalchemy import Column, BigInteger, DateTime
from sqlalchemy.sql import func

from app.core.database import Base

class Favorite(Base):
    __tablename__ = "favorites"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    product_id = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, server_default=func.now())