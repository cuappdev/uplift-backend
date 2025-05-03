from sqlalchemy import Column, Integer, ForeignKey, TIME, Boolean
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import Enum as SQLAEnum
from src.models.enums import DayOfWeekEnum
from src.database import Base

class WorkoutReminder(Base):
    """
    A workout reminder for an Uplift user.
    Attributes:
        - `id`                                    The ID of the workout reminder.
        - `user_id`                               The ID of the user who owns this reminder.
        - `days_of_week`                          The days of the week when the reminder is active.
        - `reminder_time`                         The time of day the reminder is scheduled for.
        - `is_active`                             Whether the reminder is currently active (default is True).
    """

    __tablename__ = "workout_reminder"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    days_of_week = Column(ARRAY(SQLAEnum(DayOfWeekEnum)), nullable=False)
    reminder_time = Column(TIME, nullable=False)
    is_active = Column(Boolean, default=True)