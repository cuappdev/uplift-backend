import datetime
from typing import Counter
from database import Base
from sqlalchemy import Table, Column, Integer, DateTime, ForeignKey, String, Boolean, null
from sqlalchemy.orm import relationship

activities_to_gyms = Table(
    "activities_to_gyms",
    Base.metadata,
    Column("gym_id", ForeignKey("gym.id"), primary_key=True),
    Column("activity_id", ForeignKey("activity.id"), primary_key=True),
)


class Activity(Base):
    __tablename__ = "activity"

    id = Column(Integer, primary_key=True)
    name = Column(String(), nullable=False)
    details = Column(String(1000), nullable=False)
    gyms = relationship('Gym', secondary=activities_to_gyms,
                        back_populates="activities")
    prices = relationship('Price', cascade='delete, all')
    amenities = relationship('Amenity', cascade='delete, all')
    image_url = Column(String(1000), nullable=True)

    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.details = kwargs.get("details")
        self.image_url = kwargs.get("image_url")


class Price(Base):
    __tablename__ = "price"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    cost = Column(Integer, nullable=False)
    one_time = Column(Boolean, nullable=False)
    image_url = Column(String(1000), nullable=True)
    activity_id = Column(Integer, ForeignKey('activity.id'), nullable=False)

    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.cost = kwargs.get("cost")
        self.one_time = kwargs.get("one_time")
        self.image_url = kwargs.get("image_url")
        self.activity_id = kwargs.get("activity_id")


class Amenity(Base):
    __tablename__ = 'amenity'

    id = Column(Integer, primary_key=True)
    name = Column(String(), nullable=False)
    image_url = Column(String(), nullable=True)
    activity_id = Column(Integer, ForeignKey('activity.id'), nullable=False)

    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.image_url = kwargs.get("image_url")
        self.activity_id = kwargs.get("activity_id")
