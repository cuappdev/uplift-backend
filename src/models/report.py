from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Enum
from sqlalchemy.orm import relationship
from src.database import Base
import enum

class ReportType(enum.Enum):
    INACCURATE_EQUIPMENT = 0
    INCORRECT_HOURS = 1
    INACCURATE_DESCRIPTION = 2
    WAIT_TIMES_NOT_UPDATED = 3
    OTHER = 4

class Report(Base):
    """
    A report object.

    Attributes:
        - `id`              The ID of the report.
        - `user_id`         The ID of the user who created the report.
        - `issue`           The issue reported (discrete options).
        - `description`     The description of the report.
        - `created_at`      The date and time the report was created.
        - `gym_id`          The ID of the gym associated with the report.
    """

    __tablename__ = "report"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False)  # Timestamp for user submission
    description = Column(String, nullable=False)  # Text input
    gym_id = Column(Integer, ForeignKey("gym.id"), nullable=False)  # One to many relationship with gym
    issue = Column(Enum(ReportType), nullable=False)  # Discrete options (enumerate)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # Make relationship with gym and user
    gym = relationship("Gym", back_populates="reports")
    user = relationship("User", back_populates="reports")
