import sys
sys.path.append('..')
import enum
from sqlalchemy import Column, ForeignKey, String, Enum, Integer
from sqlalchemy.orm import relationship
from src.database import Base
from src.models.capacity import Capacity



class FacilityType(enum.Enum):
    fitness = 0


class Facility(Base):
    __tablename__ = "facility"

    id = Column(Integer, primary_key=True)
    gym_id = Column(Integer, ForeignKey("gym.id"), nullable=False)
    name = Column(String(), nullable=False)
    facility_type = Column(Enum(FacilityType), nullable=False)
    open_hours = relationship("OpenHours")
    capacities = relationship("Capacity")

    # TODO: - Implement the following
    # image_url = Column(String(1000), nullable=True)

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.gym_id = kwargs.get("gym_id")
        self.facility_type = kwargs.get("facility_type")

        # TODO: - Implement the following
        # self.image_url = kwargs.get("image_url")

    # def serialize(self):
    #     return {
    #         "id": self.id,
    #         "name": self.name,
    #         "gym_id": self.gym_id,
    #         "facility_type": self.facility_type,
    #         "capacities": self.capacities,
    #     }


# Left here as a reference for the above TODOs


"""
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


    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.image_url = kwargs.get("image_url")
        self.activity_id = kwargs.get("activity_id")
"""