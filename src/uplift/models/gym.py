import datetime
from database import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Float, String, Boolean, func
from sqlalchemy.orm import backref, relationship


class Gym(Base):
    __tablename__ = "gym"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(1000), nullable=False)
    # activities = relation
    # facilties = relation
    times = relationship('GymTime', cascade='delete, all')
    capacity = relationship('Capacity', cascade='delete, all')
    location=Column(String(1000), nullable=False)
    latitude=Column(Integer, nullable=False)
    longitude=Column(Float, nullable=False)
    image_url = Column(String(1000), nullable=True)

    # equipment 
    # amenities
    # cost_type
    # activities
    # image_url
    # popular_times

    def __init__(self, **kwargs):
        self.id=kwargs.get("id")
        self.name = kwargs.get("name")
        self.description = kwargs.get("description")
        self.location = kwargs.get('location')
        self.latitude = kwargs.get('latitude')
        self.longitude = kwargs.get('longitude')
        self.image_url = kwargs.get("image_url")

    def serialize(self):
        return {
            "id":self.id,
            "name": self.name,
            "description": self.description,
            #"times": self.times,
            "location": self.location,
            "latitude": self.latitude,
            "longitude":self.longitude,
            "image_url": self.image_url
        }


class GymTime(Base):
    __tablename__ = 'gymtime'

    id = Column(Integer, primary_key=True)
    daytime_id = Column(Integer, ForeignKey('daytime.id'), nullable=False)
    gym_id = Column(Integer, ForeignKey('gym.id'), nullable=False)

    def __init__(self, **kwargs):
        self.daytime_id = kwargs.get("daytime_id")
        self.gym_id = kwargs.get("gym_id")

    def serialize(self):
        return {
            "daytime_id": self.daytime_id,
            "gym_id": self.gym_id
        }