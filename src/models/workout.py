"""Persist individual gym check-ins and their timestamps."""

from sqlalchemy import Column, Integer, ForeignKey, DateTime, text, Index
from sqlalchemy.orm import relationship
from src.database import Base


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
    __table_args__ = (Index("ix_workout_user_time", "user_id", "workout_time"),)

    id = Column(Integer, primary_key=True)
    workout_time = Column(
        DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )  # should this be nullable?
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    facility_id = Column(Integer, ForeignKey("facility.id"), nullable=False)

    user = relationship("User", back_populates="workouts")
