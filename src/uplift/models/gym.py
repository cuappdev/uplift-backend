import datetime
from database import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Float, String, Boolean, func
from sqlalchemy.orm import backref, relationship
from models.facility import Facility
from models.activity import activities_to_gyms


class Gym(Base):
    __tablename__ = "gym"

    id = Column(Integer, primary_key=True)
    name = Column(String(), nullable=False)
    description = Column(String(), nullable=False)
    activities = relationship("Activity", secondary=activities_to_gyms, back_populates="gyms")
    facilities = relationship("Facility", cascade="delete, all")
    times = relationship("GymTime", cascade="delete, all")
    capacity = relationship("Capacity", cascade="delete, all")
    location = Column(String(), nullable=False)
    latitude = Column(Integer, nullable=False)
    longitude = Column(Float, nullable=False)
    image_url = Column(String(), nullable=True)

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.description = kwargs.get("description")
        self.location = kwargs.get("location")
        self.latitude = kwargs.get("latitude")
        self.longitude = kwargs.get("longitude")
        self.image_url = kwargs.get("image_url")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "location": self.location,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "image_url": self.image_url,
        }


class GymTime(Base):
    __tablename__ = "gymtime"

    id = Column(Integer, primary_key=True)
    daytime_id = Column(Integer, ForeignKey("daytime.id"), nullable=False)
    gym_id = Column(Integer, ForeignKey("gym.id"), nullable=False)

    def __init__(self, **kwargs):
        self.daytime_id = kwargs.get("daytime_id")
        self.gym_id = kwargs.get("gym_id")

    def serialize(self):
        return {"daytime_id": self.daytime_id, "gym_id": self.gym_id}
