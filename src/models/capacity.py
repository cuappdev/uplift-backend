from sqlalchemy import Column, ForeignKey, Integer, DateTime, Float, Identity, String
from sqlalchemy.orm import backref, relationship
from src.database import Base 
"""
Store counts for each Gym
"""

class Capacity(Base):
  __tablename__ = 'capacity'

  id = Column(Integer, Identity(1, 1), primary_key = True)
  facility_id = Column(String(40), ForeignKey('facility.id'), nullable=False)
  count = Column(Integer, nullable=False)
  percent = Column(Float, nullable=False)
  updated = Column(DateTime, nullable=False)

  def __init__(self, **kwargs):
    self.facility_id = kwargs.get("facility_id")
    self.count = kwargs.get("count")
    self.percent = kwargs.get("percent")
    self.updated = kwargs.get("updated")

  def serialize(self):
    return {
      "facility_id": self.facility_id,
      "count": self.count,
      "percent": self.percent,
      "updated": self.updated
    }