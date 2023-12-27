import enum
from sqlalchemy import Boolean, Column, Enum, Integer, Float, ForeignKey
from src.database import Base


class CourtType(enum.Enum):
    """
    An enumeration representing a court type.
    """

    basketball = 0
    volleyball = 1
    badminton = 2


class OpenHours(Base):
    """
    A facility or gym's open hours.

    Attributes:
        - `id`            The ID of these hours.
        - `court_type`    (nullable) The type of this court for these hours, if applicable.
        - `end_time`      The Unix time of when this facility closes for this day.
        - `facility_id`   (nullable) The ID of the facility for these hours, if applicable.
        - `gym_id`        (nullable) The ID of the gym for these hours, if applicable.
        - `is_shallow`    (nullable) True if these hours are for shallow waters only
        - `is_special`    True if these hours are special (non-regular). Default is False.
        - `is_women`      (nullable) True if these hours are for women only.
        - `start_time`    The Unix time of when this facility opens for this day.
    """

    __tablename__ = "openhours"

    id = Column(Integer, primary_key=True)
    court_type = Column(Enum(CourtType), nullable=True)
    end_time = Column(Integer, nullable=False)
    facility_id = Column(Integer, ForeignKey("facility.id"), nullable=True)
    gym_id = Column(Integer, ForeignKey("gym.id"), nullable=True)
    is_shallow = Column(Boolean, nullable=True)
    is_special = Column(Boolean, nullable=False)
    is_women = Column(Boolean, nullable=True)
    start_time = Column(Integer, nullable=False)

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.court_type = kwargs.get("court_type")
        self.end_time = kwargs.get("end_time")
        self.facility_id = kwargs.get("facility_id")
        self.gym_id = kwargs.get("gym_id")
        self.is_shallow = kwargs.get("is_shallow")
        self.is_special = kwargs.get("is_special", False)
        self.is_women = kwargs.get("is_women")
        self.start_time = kwargs.get("start_time")

    def serialize(self):
        return {
            "id": self.id,
            "court_type": self.court_type,
            "end_time": self.end_time,
            "facility_id": self.facility_id,
            "gym_id": self.gym_id,
            "is_shallow": self.is_shallow,
            "is_special": self.is_special,
            "is_women": self.is_women,
            "start_time": self.start_time,
        }
