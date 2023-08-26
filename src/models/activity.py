import enum
from sqlalchemy import Column, ForeignKey, String, Enum
from sqlalchemy.orm import relationship
from src.database import Base


class ActivityType(enum.Enum):
    fitness = 0
    basketball = 1

class Activity(Base):
    __tablename__ = "activity"

    id = Column(String(40), primary_key=True)
    name = Column(String(), nullable=False)
    activity_type = Column(Enum(ActivityType), nullable=False)
    gym_id = Column(String(40), ForeignKey('gym.id'), nullable=False)
    open_hours = relationship("OpenHours")

    # TODO: - Implement the following
    # prices = relationship('Price', cascade='delete, all')
    # amenities = relationship('Amenity', cascade='delete, all')
    # image_url = Column(String(1000), nullable=True)

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.gym_id = kwargs.get("gym_id")
        self.activity_type = kwargs.get("activity_type")

        # TODO: - Implement the following
        # self.image_url = kwargs.get("image_url")

    def serialize(self):
        return {
            "id":self.id,
            "name": self.name,
            "gym_id": self.gym_id,
            "activity_type": self.activity_type,
        }


# Left here as a reference for the above TODOs

"""
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
"""