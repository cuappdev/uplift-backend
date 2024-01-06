from sqlalchemy import Column, Integer, Float, ForeignKey
from src.database import Base


class Capacity(Base):
    """
    Store counts for a Facility.

    Attributes:
        - `id`              The ID of this capacity.
        - `count`           The number of people in the facility.
        - `facility_id`     The ID of the facility this capacity belongs to.
        - `percent`         The percent filled between 0.0 and 1.0.
        - `updated`         The Unix time since this capacity was last updated.
    """

    __tablename__ = "capacity"

    id = Column(Integer, primary_key=True)
    count = Column(Integer, nullable=False)
    facility_id = Column(Integer, ForeignKey("facility.id"), nullable=False)
    percent = Column(Float, nullable=False)
    updated = Column(Integer, nullable=False)

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.count = kwargs.get("count")
        self.facility_id = kwargs.get("facility_id")
        self.percent = kwargs.get("percent")
        self.updated = kwargs.get("updated")

    def serialize(self):
        return {
            "id": self.id,
            "count": self.count,
            "facility_id": self.facility_id,
            "percent": self.percent,
            "updated": self.updated,
        }
