import enum
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float, Enum
from sqlalchemy.orm import relationship
from src.database import Base


class PriceType(enum.Enum):
    """
    An enumeration representing a price type.
    """

    rate = 0
    gear = 1


class Activity(Base):
    """
    Activity provided by a recreation center.

    Attributes:
        - `id`              The ID of this activity.
        - `facility_id`     The ID of the facility this activity belongs to.
        - `gear`            (nullable) This activity's gear.
        - `gym_id`          The ID of the gym this activity belongs to.
        - `has_membership   True if this activity is available with memberships.
        - `name`            The name of this activity.
        - `needs_reserve`   True if this activity requires group reservation.
        - `pricing`         (nullable) This activity's pricing.
    """

    __tablename__ = "activity"

    id = Column(Integer, primary_key=True)
    facility_id = Column(Integer, ForeignKey("facility.id"), nullable=False)
    gear = relationship("Gear", cascade="delete")
    gym_id = Column(Integer, ForeignKey("gym.id"), nullable=False)
    has_membership = Column(Boolean, nullable=False)
    name = Column(String, nullable=False)
    needs_reserve = Column(Boolean, nullable=False)
    pricing = relationship("Price", cascade="delete")

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.facility_id = kwargs.get("facility_id")
        self.gym_id = kwargs.get("gym_id")
        self.has_membership = kwargs.get("has_membership")
        self.name = kwargs.get("name")
        self.needs_reserve = kwargs.get("needs_reserve")

    def serialize(self):
        return {
            "id": self.id,
            "facility_id": self.facility_id,
            "gear": self.gear,
            "gym_id": self.gym_id,
            "has_membership": self.has_membership,
            "name": self.name,
            "needs_reserve": self.needs_reserve,
            "pricing": self.pricing,
        }


class Price(Base):
    """
    The price of a gear or pricing option.

    Attributes:
        - `id`              The ID of this price.
        - `activity_id`     The ID of the activity this price belongs to.
        - `name`            The name associated with this price.
        - `cost`            The cost of this price.
        - `rate`            (nullable) The pricing rate of this price.
        = `type`            The type of this price.
    """

    __tablename__ = "gear"

    id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, ForeignKey("activity.id"), nullable=False)
    name = Column(String, nullable=False)
    cost = Column(Float, nullable=-False)
    rate = Column(String)
    type = Column(Enum(PriceType), nullable=False)

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.activity_id = kwargs.get("activity_id")
        self.name = kwargs.get("name")
        self.cost = kwargs.get("price")
        self.rate = kwargs.get("rate")
        self.type = kwargs.get("type")

    def serialize(self):
        return {
            "id": self.id,
            "activity_id": self.activity_id,
            "name": self.name,
            "cost": self.cost,
            "rate": self.rate,
            "type": self.type,
        }
