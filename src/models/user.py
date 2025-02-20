from sqlalchemy import Column, Integer, String, ARRAY, Enum
from sqlalchemy.orm import backref, relationship
from src.database import Base
from src.models.enums import DayOfWeekEnum

class User(Base):
    """
    An uplift user.

    Attributes:
        - `id`                                    The ID of user.
        - `email`                                 The user's email address.
        - `giveaways`                             (nullable) The list of giveaways a user is entered into.
        - `net_id`                                The user's Net ID.
        - `name`                                  The user's name.
        - `workout_goal`                          The days of the week the user has set as their personal goal.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=True)
    giveaways = relationship("Giveaway", secondary="giveaway_instance", back_populates="users")
    net_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    workout_goal = Column(ARRAY(Enum(DayOfWeekEnum)), nullable=True)
