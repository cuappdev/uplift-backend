from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.database import Base


class User(Base):
    """
    An uplift user.

    Attributes:
        - `id`              The ID of user.
        - `giveaways`       (nullable) The list of giveaways a user is entered into.
        - `instagram`       (nullable) The username handle of this user's Instagram.
        - `net_id`          The user's Net ID.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    giveaways = relationship("Giveaway", secondary="giveaway_instance", back_populates="users")
    reports = relationship("Report", back_populates="user")
    instagram = Column(String, nullable=True)
    net_id = Column(String, nullable=False)
