import datetime
from database import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Boolean, func
from sqlalchemy.orm import backref, relationship

class Gym(Base):
    __tablename__ = "gym"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(1000), nullable=False)
    # activities = so fun
    # popular ????
    times = relationship('DayTime', cascade='delete, all')
    image_url = Column(String(1000), nullable=True)

    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.description = kwargs.get("description")
        self.image_url = kwargs.get("image_url")

    def serialize(self):
        return {
            "name": self.name,
            "description": self.description,
            "times": self.times,
            "image_url": self.image_url
        }


class DayTime(Base):
    __tablename__ = "daytime"

    id = Column(Integer, primary_key=True)
    day = Column(Integer, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    restrictions = Column(String(1000))
    special_hours = Column(Boolean, nullable=False)
    gym_id = Column(Integer, ForeignKey('gym.id'), nullable=False)

    def __init__(self, **kwargs):
        self.day = kwargs.get("day")
        self.start_time = kwargs.get("start_time")
        self.end_time = kwargs.get("end_time")
        self.restrictions = kwargs.get("restrictions")
        self.special_hours = kwargs.get("special_hours")
        self.gym_id = kwargs.get("gym_id")

    def serialize(self):
        return {
            "day": self.day,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "restrictions": self.restrictions,
            "special_hours": self.special_hours,
            "gym_id": self.gym_id
        }
