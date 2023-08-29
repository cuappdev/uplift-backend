from database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime
from sqlalchemy.orm import backref, relationship

"""
Store counts for each Gym
"""


class Capacity(Base):
    __tablename__ = "capacity"
    id = Column(Integer, primary_key=True)
    gym_id = Column(Integer, ForeignKey("gym.id"), nullable=False)
    count = Column(Integer, nullable=False)
    updated = Column(DateTime, nullable=False)

    def __init__(self, **kwargs):
        self.gym_id = kwargs.get("gym_id")
        self.count = kwargs.get("count")
        self.updated = kwargs.get("updated")

    def serialize(self):
        return {"gym_id": self.gym_id, "count": self.count, "updated": self.updated}
