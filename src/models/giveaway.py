from sqlalchemy import Column, Integer, Float, ForeignKey, String
from sqlalchemy.orm import relationship
from src.database import Base
from src.models.user import User


class Giveaway(Base):
    """
    A giveaway object.

    Attributes:
        - `id`              The ID of the giveaway.
        - `name`            The name of the giveaway.
        - `user_ids`        (nullable) The IDs of users entered into this giveaway.
    """

    __tablename__ = "giveaway"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    user_ids = relationship("GiveawayInstance", back_populates="users")

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.user_ids = kwargs.get("user_id")

    def serialize(self):
        return {"id": self.id, "name": self.name, "user_ids": self.user_ids}


class GiveawayInstance(Base):
    """
    An entry into a giveaway.

    Attributes:
        - `id`                 The ID of the giveaway entry.
        - `giveaway_id`        The ID of the giveaway.
        - `user_id`            The ID of the user entered into the giveaway.
        - `numEntries`         The number of entries of this user into the giveaway.
    """

    __tablename__ = "giveaway_instance"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    giveaway_id = Column(Integer, ForeignKey("giveaway.id"), nullable=False)
    num_entries = Column(Integer, nullable=False)
