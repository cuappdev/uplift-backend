from sqlalchemy import Column, ForeignKey, Integer, String, Float
from src.database import Base

class OpenHours(Base):
    __tablename__ = "openhours"

    id = Column(String(), primary_key=True)
    facility_id = Column(String(40), ForeignKey("facility.id"), nullable=False)
    day = Column(Integer, nullable=False)
    start_time = Column(Float, nullable=False) # TODO: - Convert to DateTime
    end_time = Column(Float, nullable=False)
    # TODO: - Handle restrictions and special hours
    # restrictions = Column(String(1000))
    # special_hours = Column(Boolean, nullable=False)

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.facility_id = kwargs.get("facility_id")
        self.day = kwargs.get("day")
        self.start_time = kwargs.get("start_time")
        self.end_time = kwargs.get("end_time")
        # TODO: - Handle restrictions and special hours
        # self.restrictions = kwargs.get("restrictions")
        # self.special_hours = kwargs.get("special_hours")

    def serialize(self):
        return {
            "id": self.id,
            "facility_id": self.activity_id,
            "day": self.day,
            "start_time": self.start_time,
            "end_time": self.end_time,
            # TODO: - Handle restrictions and special hours
            # "restrictions": self.restrictions,
            # "special_hours": self.special_hours
        }