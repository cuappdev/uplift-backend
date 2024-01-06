import enum
from sqlalchemy import Column, Enum, Integer, ForeignKey
from src.database import Base


class AmenityType(enum.Enum):
    """
    An enumeration representing an amenity type.
    """

    showers = 0
    lockers = 1
    parking = 2
    elevators = 3


class Amenity(Base):
    """
    Amenity provided by a Gym.

    Attributes:
        - `id`          The ID of this amenity.
        - `gym_id`      The ID of the gym with this amenity.
        - `type`        The type of this amenity such as showers, lockers, etc.
    """

    __tablename__ = "amenity"

    id = Column(Integer, primary_key=True)
    gym_id = Column(Integer, ForeignKey("gym.id"), nullable=False)
    type = Column(Enum(AmenityType), nullable=False)

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.gym_id = kwargs.get("gym_id")
        self.type = kwargs.get("type")

    def serialize(self):
        return {"id": self.id, "gym_id": self.gym_id, "type": self.type}
