<<<<<<< HEAD:src/models/facility.py
<<<<<<<< HEAD:src/models/facility.py
import enum
from sqlalchemy import Column, ForeignKey, String, Enum, Integer
========
import datetime
from importlib.machinery import FrozenImporter
from typing import Counter
from database import Base
from sqlalchemy import Table, Column, Integer, DateTime, ForeignKey, String, Boolean, null
>>>>>>>> 2eebca9 (almost implementing Facilities):src/uplift/models/activity.py
from sqlalchemy.orm import relationship
from src.database import Base
from src.models.openhours import OpenHours
from src.models.capacity import Capacity


class FacilityType(enum.Enum):
    fitness = 0


class Facility(Base):
    __tablename__ = "facility"

    id = Column(Integer, primary_key=True)
    gym_id = Column(Integer, ForeignKey("gym.id"), nullable=False)
    name = Column(String(), nullable=False)
<<<<<<<< HEAD:src/models/facility.py
    facility_type = Column(Enum(FacilityType), nullable=False)
    open_hours = relationship("OpenHours")
    capacities = relationship("Capacity")

    # TODO: - Implement the following
    # prices = relationship('Price', cascade='delete, all')
    # amenities = relationship('Amenity', cascade='delete, all')
    # image_url = Column(String(1000), nullable=True)
========
    details = Column(String(), nullable=False)
    gyms = relationship('Gym', secondary=activities_to_gyms,
                        back_populates="activities")
    prices = relationship('ActivityPrice', cascade='delete, all')
    amenities = relationship('Amenity', cascade='delete, all')
    image_url = Column(String(), nullable=True)
>>>>>>>> 2eebca9 (almost implementing Facilities):src/uplift/models/activity.py

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.gym_id = kwargs.get("gym_id")
        self.facility_type = kwargs.get("facility_type")

        # TODO: - Implement the following
        # self.image_url = kwargs.get("image_url")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "gym_id": self.gym_id,
            "facility_type": self.facility_type,
            "capacities": self.capacities,
        }

<<<<<<<< HEAD:src/models/facility.py

# Left here as a reference for the above TODOs

"""
class Price(Base):
    __tablename__ = "price"
========
class ActivityPrice(Base):
    __tablename__ = "activityprice"
>>>>>>>> 2eebca9 (almost implementing Facilities):src/uplift/models/activity.py

    id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, ForeignKey('activity.id'), nullable=False)
    price_id = Column(Integer, ForeignKey('price.id'), nullable=False)

    def __init__(self, **kwargs):
        self.activity_id = kwargs.get("activity_id")
        self.price = kwargs.get("price_id")

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
"""
=======
from ast import For
from database import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Float, String, func
from sqlalchemy.orm import backref, relationship
from models.price import Price


class Facility(Base):
  __tablename__ = "facility"

  id = Column(Integer, primary_key=True)
  name = Column(String(), nullable=False)
  times = relationship('FacilityTime', cascade='delete, all')
  price = relationship('Price', cascade='delete, all')
  equipment = relationship('Equipment', cascade='delete, all') 
  image_url = Column(String(), nullable=True)

  def __init__(self, **kwargs):
    self.name = kwargs.get("name")
    self.image_url = kwargs.get("image")


class FacilityTime(Base):
  __tablename__ = "facilitytime"

  id = Column(Integer, primary_key=True)
  facilty_id = Column(Integer, ForeignKey('facility.id'), nullable=False)
  daytime_id = Column(Integer, ForeignKey('daytime.id'), nullable=False)

  def __init__(self, **kwargs):
    self.facility_id = kwargs.get("facility_id")
    self.daytime_id = kwargs.get("daytime_id")

class FacilityPrice(Base):
  __tablename__ = "facilityprice"

  id = Column(Integer, primary_key=True)
  facility_id = Column(Integer, ForeignKey('facility.id'), nullable=False)
  price_id = Column(Integer, ForeignKey('price.id'), nullable=False)

  def __init__(self, **kwargs):
    self.facility_id=kwargs.get("facility_id")
    self.price_id=kwargs.get("price_id")


class Equipment(Base):
  __tablename__ = "equipment"

  id = Column(Integer, primary_key=True)
  equipment_type = Column(String(), nullable=False)
  name = Column(String(), nullable=False)
  quantity = Column(Integer, nullable=False)
  facility_id = Column(Integer, ForeignKey('facility.id'), nullable=False)

  def __init__(self, **kwargs):
    self.equipment_type = kwargs.get("equipment_type")
    self.name = kwargs.get("name")
    self.quantity = kwargs.get("quantity")
    self.facility_id=kwargs.get("facility_id")







>>>>>>> 2eebca9 (almost implementing Facilities):src/uplift/models/facility.py
