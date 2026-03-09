from sqlalchemy import Column, Integer, Float, ForeignKey, String, DateTime, text
from sqlalchemy.orm import backref, relationship
from src.database import Base
from datetime import timezone


class Workout(Base):
    """
    A workout logged by a user.

    Attributes:
        - `id`              The ID of the workout.
        - `workout_time`    The date and time of the workout.
        - `user_id`         The ID of the user who completed the workout.
        - `facility_id`     The ID of the facility visited
    """

    __tablename__ = "workout"

    id = Column(Integer, primary_key=True)
    workout_time = Column(DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))  # should this be nullable?
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    facility_id = Column(Integer, ForeignKey("facility.id"), nullable=False)
