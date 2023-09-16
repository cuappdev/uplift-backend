import datetime
from importlib.machinery import FrozenImporter
from typing import Counter
from database import Base
from sqlalchemy import (
    Table,
    Column,
    Integer,
    DateTime,
    ForeignKey,
    String,
    Boolean,
    null,
)
from sqlalchemy.orm import relationship

activities_to_gyms = Table(
    "activities_to_gyms",
    Base.metadata,
    Column("id", primary_key=True),
    Column("gym_id", ForeignKey("gym.id")),
    Column("activity_id", ForeignKey("activity.id")),
)


class Activity(Base):
    __tablename__ = "activity"

    id = Column(Integer, primary_key=True)
    name = Column(String(), nullable=False)
    details = Column(String(), nullable=False)
    gyms = relationship(
        "Gym", secondary=activities_to_gyms, back_populates="activities"
    )
    prices = relationship("ActivityPrice", cascade="delete, all")
    amenities = relationship("Amenity", cascade="delete, all")
    image_url = Column(String(), nullable=True)

    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.details = kwargs.get("details")
        self.image_url = kwargs.get("image_url")


class ActivityPrice(Base):
    __tablename__ = "activityprice"

    id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, ForeignKey("activity.id"), nullable=False)
    price_id = Column(Integer, ForeignKey("price.id"), nullable=False)

    def __init__(self, **kwargs):
        self.activity_id = kwargs.get("activity_id")
        self.price = kwargs.get("price_id")


class Amenity(Base):
    __tablename__ = "amenity"

    id = Column(Integer, primary_key=True)
    name = Column(String(), nullable=False)
    image_url = Column(String(), nullable=True)
    activity_id = Column(Integer, ForeignKey("activity.id"), nullable=False)

    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.image_url = kwargs.get("image_url")
        self.activity_id = kwargs.get("activity_id")
