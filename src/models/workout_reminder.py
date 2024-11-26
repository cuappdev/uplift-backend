from sqlalchemy import Column, Integer, ForeignKey, TIME, Boolean
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import Enum as SQLAEnum
from src.models.user import DayOfWeekEnum
from src.database import Base

class WorkoutReminder(Base):
    __tablename__ = "workout_reminder"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    days_of_week = Column(ARRAY(SQLAEnum(DayOfWeekEnum)), nullable=False)
    reminder_time = Column(TIME, nullable=False)
    is_active = Column(Boolean, default=True)
