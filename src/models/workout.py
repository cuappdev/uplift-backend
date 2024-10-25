from sqlalchemy import Column, Integer, Float, ForeignKey, String, DateTime
from sqlalchemy.orm import backref, relationship
from src.database import Base


class Workout(Base):
    """
    A workout logged by a user.

    Attributes:
        - `id`              The ID of user.
        - `workout_time`    The date and time of the workout.
        - `user_id`         The ID of the user who completed the workout.
    """

    __tablename__ = "workout"

    id = Column(Integer, primary_key=True)
    workout_time = Column(DateTime(), nullable=False)  # should this be nullable?
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
