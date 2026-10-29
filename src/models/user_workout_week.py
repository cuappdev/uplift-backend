"""Stored progress for one user's Monday-Sunday week."""
from sqlalchemy import Boolean, CheckConstraint, Column, Date, ForeignKey, Integer, Index
from src.database import Base


class UserWorkoutWeek(Base):
    __tablename__ = "user_workout_week"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    week_start = Column(Date, primary_key=True)
    workout_goal = Column(Integer, nullable=False, default=1)
    # Bit 0 is Monday, bit 6 is Sunday. A repeated check-in sets the same bit.
    checked_in_days = Column(Integer, nullable=False, default=0)
    goal_awarded = Column(Boolean, nullable=False, default=False)
    finalized = Column(Boolean, nullable=False, default=False)

    __table_args__ = (
        Index("ix_workout_week_pending", "finalized", "week_start", "user_id"),
        CheckConstraint("checked_in_days BETWEEN 0 AND 127", name="ck_workout_week_days"),
        CheckConstraint("workout_goal BETWEEN 1 AND 7", name="ck_workout_week_goal"),
    )
