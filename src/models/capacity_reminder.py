from sqlalchemy import Column, Integer, ForeignKey, ARRAY
from sqlalchemy import Enum as SQLAEnum
from src.models.enums import DayOfWeekEnum
from src.database import Base

class CapacityReminder(Base):
    __tablename__ = "capacity_reminder"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    gym_id = Column(Integer, ForeignKey("gym.id"), nullable=False)
    capacity_threshold = Column(Integer, nullable=False)
    days_of_week = Column(ARRAY(SQLAEnum(DayOfWeekEnum)), nullable=False)