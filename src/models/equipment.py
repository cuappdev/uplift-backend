import enum
from sqlalchemy import Column, String, Enum, Integer, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from src.database import Base


class MuscleGroup(enum.Enum):
    ABDOMINALS = 1  # Core/Ab exercises
    CHEST = 2       # Chest exercises
    BACK = 3        # Back exercises
    SHOULDERS = 4   # Shoulder exercises
    BICEPS = 5      # Bicep exercises
    TRICEPS = 6     # Tricep exercises
    HAMSTRINGS = 7  # Hamstring exercises
    QUADS = 8       # Quad exercises
    GLUTES = 9      # Glute exercises
    CALVES = 10     # Calf exercises
    MISCELLANEOUS = 11  # General equipment, accessories, and multi-purpose items
    CARDIO = 12     # Cardiovascular equipment


class AccessibilityType(enum.Enum):

    wheelchair = 0

class Equipment(Base):

    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    muscle_groups = Column(ARRAY(Enum(MuscleGroup)), nullable=False)
    clean_name = Column(String, nullable=False)
    facility_id = Column(Integer, ForeignKey("facility.id"), nullable=False)
    quantity = Column(Integer, nullable=True)
    accessibility = Column(Enum(AccessibilityType), nullable=True)

def __init__(self, **kwargs):
    self.id = kwargs.get("id")
    self.name = kwargs.get("name")
    self.muscle_groups = kwargs.get("muscle_groups")
    self.facility_id = kwargs.get("facility_id")
    self.quantity = kwargs.get("quantity")
    self.accessibility = kwargs.get("accessibility")
