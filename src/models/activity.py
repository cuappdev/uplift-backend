from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from src.database import Base

class Activity(Base):
    """
    Activity provided by a recreation center.

    Attributes:
        - `id`              The ID of this activity.
        - `name`            The name of this activity.
        - `facility_id`     The ID of the facility this activity belongs to.
        - `gym_id`          The ID of the gym this activity belongs to.
        - `one_time_price`  The one-time price of this activity.
        - `needs_reserve`   True if this activity requires group reservation.
        - `gear`            (nullable) This activity's gear.
    """

    __tablename__ = "activity"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    facility_id = Column(Integer, ForeignKey("facility.id"), nullable=False)
    gym_id = Column(Integer, ForeignKey("gym.id"), nullable=False)
    one_time_price = Column(Boolean, nullable=False)
    needs_reserve = Column(Boolean, nullable=False)
    gear = relationship("Gear", cascade="delete")

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.facility_id = kwargs.get("facility_id")
        self.gym_id = kwargs.get("gym_id")
        self.one_time_price = kwargs.get("one_time_price")
        self.needs_reserve = kwargs.get("needs_reserve")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "facility_id": self.facility_id,
            "gym_id": self.gym_id,
            "one_time_price": self.one_time_price,
            "needs_reserve": self.needs_reserve,
            "gear": self.gear
        }
    
    
class Gear(Base):
    """
    Gear required for an activity

    Attributes:
    - `id`              The ID of this gear
    - `name`            The name of this gear
    - `price`           The price of this gear
    - `activity_id`     The ID of the activity this gear belongs to
    """

    __tablename__ = "gear"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=-False)
    activity_id = Column(Integer, ForeignKey("activity.id"), nullable=False)

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.price = kwargs.get("price")
        self.activity_id = kwargs.get("activity_id")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price
        }
