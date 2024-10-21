from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from src.database import Base


class Giveaway(Base):
    """
    A giveaway object.

    Attributes:
        - `id`              The ID of the giveaway.
        - `name`            The name of the giveaway.
        - `users`           (nullable) The users that entered into this giveaway.
    """

    __tablename__ = "giveaway"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    users = relationship("User", secondary="giveaway_instance", back_populates="giveaways")


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
