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







