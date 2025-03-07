from sqlalchemy import Column, String, Integer, DateTime
from src.database import Base


class TokenBlocklist(Base):
    """
    Represents a JWT token that has been revoked (blacklisted).

    Attributes:
        - `id`          The primary key of the token record.
        - `jti`         The unique identifier (JWT ID) of the token. Indexed for fast lookup.
        - `expires_at`  The DateTime when the token expires.
    """

    __tablename__ = "token_blacklist"

    id = Column(Integer, primary_key=True)
    jti = Column(String(36), index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
