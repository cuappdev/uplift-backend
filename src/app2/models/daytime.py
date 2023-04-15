import datetime
from database import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Boolean, func
from sqlalchemy.orm import backref, relationship
from models.gym import Gym, GymTime

class DayTime(Base):
    __tablename__ = "daytime"

    id = Column(Integer, primary_key=True)
    day = Column(Integer, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    restrictions = Column(String(1000))
    special_hours = Column(Boolean, nullable=False)

    def __init__(self, **kwargs):
        self.day = kwargs.get("day")
        self.start_time = kwargs.get("start_time")
        self.end_time = kwargs.get("end_time")
        self.restrictions = kwargs.get("restrictions")
        self.special_hours = kwargs.get("special_hours")

    def serialize(self):
        return {
            "day": self.day,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "restrictions": self.restrictions,
            "special_hours": self.special_hours
        }