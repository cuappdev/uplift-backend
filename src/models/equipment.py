import enum
from sqlalchemy import Column, String, Enum, Integer, ForeignKey
from sqlalchemy.orm import relationship
from src.database import Base

class EquipmentType(enum.Enum):

  cardio = 0
  racks_and_benches = 1
  selectorized = 2
  multi_cable = 3
  free_weights = 4
  miscellaneous = 5
  plate_loaded = 6


class AccessibilityType(enum.Enum):
  
  wheelchair = 0

class Equipment(Base):

  __tablename__ = "equipment"

  id = Column(Integer, primary_key=True)
  name = Column(String, nullable=False)
  equipment_type = Column(Enum(EquipmentType), nullable=False)
  facility_id = Column(Integer, ForeignKey("facility.id"), nullable=False)
  quantity = Column(Integer, nullable=True)
  accessibility = Column(Enum(AccessibilityType), nullable=True)

  def __init__(self, **kwargs):
    self.id = kwargs.get("id")
    self.name = kwargs.get("name")
    self.equipment_type = kwargs.get("equipment_type")
    self.facility_id = kwargs.get("facility_id")
    self.quantity = kwargs.get("quantity")
    self.accessibility = kwargs.get("accessibility")


