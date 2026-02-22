from sqlalchemy import Column, Integer, Float, ForeignKey, String, DateTime, text
from sqlalchemy.orm import backref, relationship
from src.database import Base
from datetime import datetime

class UserWorkoutGoalHistory(Base):
    """
    A history of a user's workout goals.

    Attributes:
        - `id`                  The ID of the user workout goal history.
        - `user_id`             The ID of the user who owns the goal history.
        - `workout_goal`        The workout goal.
        - `effective_at`        The date and time the goal was set.
    """

    __tablename__ = "user_workout_goal_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    workout_goal = Column(Integer, nullable=False)
    effective_at = Column(DateTime, nullable=False, default=datetime.utcnow, server_default=text("CURRENT_TIMESTAMP"))

    user = relationship("User", back_populates='goal_history')