from sqlalchemy import Column, Integer, Float, ForeignKey, String
from sqlalchemy.orm import backref, relationship
from src.database import Base


class User(Base):
    """
    An uplift user.

    Attributes:
        - `id`              The ID of user.
        - `giveaways`       (nullable) The list of giveaways a user is entered into.
        - `net_id`          The user's Net ID.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    giveaways = relationship("Giveaway", secondary="giveaway_instance", back_populates="users")
    net_id = Column(String, nullable=False)
