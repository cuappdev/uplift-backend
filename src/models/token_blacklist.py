from sqlalchemy import Column, Float, String, Integer, DateTime
from sqlalchemy.orm import relationship
from src.database import Base


class TokenBlocklist(Base):
    __tablename__ = "token_blacklist"

    id = Column(Integer, primary_key=True)
    jti = Column(String(36), index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
