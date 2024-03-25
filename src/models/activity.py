from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from src.database import Base


class Activity(Base):
    """
    Activity provided by a recreation center.

    Attributes:
        - `id`              The ID of this activity.
        - `facility_id`     The ID of the facility this activity belongs to.
        - `gear`            (nullable) This activity's gear.
        - `gym_id`          The ID of the gym this activity belongs to.
        - `name`            The name of this activity.
        - `needs_reserve`   True if this activity requires group reservation.
        - `one_time_price`  The one-time price of this activity.
    """

    __tablename__ = "activity"

    id = Column(Integer, primary_key=True)
    facility_id = Column(Integer, ForeignKey("facility.id"), nullable=False)
    gear = relationship("Gear", cascade="delete")
    gym_id = Column(Integer, ForeignKey("gym.id"), nullable=False)
    name = Column(String, nullable=False)
    needs_reserve = Column(Boolean, nullable=False)
    one_time_price = Column(Boolean, nullable=False)

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.facility_id = kwargs.get("facility_id")
        self.gym_id = kwargs.get("gym_id")
        self.name = kwargs.get("name")
        self.needs_reserve = kwargs.get("needs_reserve")
        self.one_time_price = kwargs.get("one_time_price")

    def serialize(self):
        return {
            "id": self.id,
            "facility_id": self.facility_id,
            "gear": self.gear,
            "gym_id": self.gym_id,
            "name": self.name,
            "needs_reserve": self.needs_reserve,
            "one_time_price": self.one_time_price,
        }


class Gear(Base):
    """
    Gear required for an activity

    Attributes:
        - `id`              The ID of this gear.
        - `activity_id`     The ID of the activity this gear belongs to.
        - `name`            The name of this gear.
        - `price`           The price of this gear.
    """

    __tablename__ = "gear"

    id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, ForeignKey("activity.id"), nullable=False)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=-False)

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.activity_id = kwargs.get("activity_id")
        self.name = kwargs.get("name")
        self.price = kwargs.get("price")

    def serialize(self):
        return {"id": self.id, "name": self.name, "price": self.price}
