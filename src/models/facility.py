import enum
from sqlalchemy import Column, String, Enum, Integer, ForeignKey
from sqlalchemy.orm import relationship
from src.database import Base


class FacilityType(enum.Enum):
    """
    An enumeration representing a facility type.
    """

    fitness = 0
    pool = 1
    bowling = 2
    court = 3


class Facility(Base):
    """
    A facility inside of a Gym.

    Attributes:
        - `id`              The ID of this facility.
        - `activities`      (nullable) The activities of this facility.
        - `capacity`        (nullable) The capacity of this facility.
        - `equipment`       (nullable) The equipment of this facility.
        - `facility_type`   The type of this facility (FITNESS, POOL, BOWLING, COURT).
        - `gym_id`          The ID of the gym this facility belongs to.
        - `hours`           (nullable) The open hours of this facility.
        - `name`            The name of this facility.
    """

    __tablename__ = "facility"

    id = Column(Integer, primary_key=True)
    activities = relationship("Activity")
    capacity = relationship("Capacity")
    equipment = relationship("Equipment")
    facility_type = Column(Enum(FacilityType), nullable=False)
    gym_id = Column(Integer, ForeignKey("gym.id"), nullable=False)
    hours = relationship("OpenHours")
    name = Column(String, nullable=False)

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.facility_type = kwargs.get("facility_type")
        self.gym_id = kwargs.get("gym_id")
        self.hours = kwargs.get("hours")
        self.name = kwargs.get("name")

    def serialize(self):
        return {
            "id": self.id,
            "capacity": self.capacity,
            "facility_type": self.facility_type,
            "gym_id": self.gym_id,
            "hours": self.hours,
            "name": self.name,
        }
