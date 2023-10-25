import enum
from sqlalchemy import Column, ForeignKey, Integer, Float, Time, String, Table, Enum
from sqlalchemy.orm import backref, relationship
from src.database import Base

openhours_restrictions = Table(
    "openhours_restrictions",
    Base.metadata,
    Column("openhour_id", ForeignKey("openhours.id"), primary_key=True),
    Column("restriction_id", ForeignKey("restrictions.id"), primary_key=True),
)
class OpenHours(Base):
    __tablename__ = "openhours"

    id = Column(Integer, primary_key=True)
    facility_id = Column(Integer, ForeignKey("facility.id"), nullable=False)
    day = Column(Integer, nullable=False) # 0=Monday, 5=Weekend
    start_time = Column(Time(), nullable=False)
    end_time = Column(Time(), nullable=False)
    # TODO: - Handle restrictions and special hours
    restrictions = relationship("Restrictions", secondary=openhours_restrictions, back_populates="openhours")
    # special_hours = Column(Boolean, nullable=False)

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.facility_id = kwargs.get("facility_id")
        self.day = kwargs.get("day")
        self.start_time = kwargs.get("start_time")
        self.end_time = kwargs.get("end_time")
        # TODO: - Handle restrictions and special hours
        self.restrictions = kwargs.get("restrictions")
        # self.special_hours = kwargs.get("special_hours")

    def serialize(self):
        return {
            "id": self.id,
            "facility_id": self.facility_id,
            "day": self.day,
            "start_time": self.start_time,
            "end_time": self.end_time,
            # TODO: - Handle restrictions and special hours
            "restrictions": self.restrictions,
            # "special_hours": self.special_hours
        }
    
class RestrictionEnum(enum.Enum):
    closed = 0
    women_only = 1
    shallow_pool_only = 2
class Restrictions(Base):
    __tablename__ = "restrictions"
    id = Column(Integer, primary_key=True)
    restriction = Column(Enum(RestrictionEnum), nullable=False)
    openhours = relationship("OpenHours", secondary=openhours_restrictions, back_populates="restrictions")

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.restriction = kwargs.get("restriction")

    def serialize(self):
        return {
            "id": self.id,
            "restriction": self.restriction,
        }
