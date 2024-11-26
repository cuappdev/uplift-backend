from sqlalchemy import Column, Integer, ForeignKey, ARRAY, Boolean, Table, String
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SQLAEnum
from src.models.enums import DayOfWeekEnum, CapacityReminderGym
from src.database import Base

class CapacityReminder(Base):
    __tablename__ = "capacity_reminder"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    gyms = Column(ARRAY(SQLAEnum(CapacityReminderGym)), nullable=False)
    capacity_threshold = Column(Integer, nullable=False)
    days_of_week = Column(ARRAY(SQLAEnum(DayOfWeekEnum)), nullable=False)
    is_active = Column(Boolean, default=True)