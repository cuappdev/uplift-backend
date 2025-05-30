from sqlalchemy import Column, Integer, Float, ForeignKey, ARRAY, Enum
from src.models.enums import DayOfWeekEnum
from src.database import Base
from sqlalchemy.types import Numeric
from decimal import Decimal


class HourlyAverageCapacity(Base):
    """
    Stores the average hourly capacity of a facility over the past 30 days.

    Attributes:
        - `id`                  The ID of the hourly capacity record.
        - `facility_id`         The ID of the facility this capacity record belongs to.
        - `average_percent`     Average percent capacity of the facility, represented as a float between 0.0 and 1.0
        - `hour_of_day`         The hour of the day this average is recorded for, in 24-hour format.
        - `day_of_week`         The day of the week this average is recorded for
        - `history`             Stores previous capacity data for this hour from (up to) the past 30 days.
    """

    __tablename__ = "hourly_average_capacity"

    id = Column(Integer, primary_key=True)
    facility_id = Column(Integer, ForeignKey("facility.id"), nullable=False)
    average_percent = Column(Float, nullable=False)
    hour_of_day = Column(Integer, nullable=False)
    day_of_week = Column(Enum(DayOfWeekEnum))
    history = Column(ARRAY(Numeric), nullable=False, default=[])

    def update_hourly_average(self, current_percent):
        new_capacity = Decimal(current_percent).quantize(Decimal('0.01'))

        if len(self.history) >= 30:
            self.history = self.history[-29:]    # Keep 29 newest records

        self.history = self.history + [new_capacity] if self.history else [new_capacity]
        
        total = 0
        for capacity in self.history:
            total += capacity
        self.average_percent = total / len(self.history)