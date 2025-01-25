from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from src.database import Base

class Checkin(Base):
    """
    A checkin object

    Attributes:
        - `id`              The ID of the checkin.
        - `created_at`      The date and time the user checked in.
        - `user_id`         The ID of the user who checked in.
        - `gym_id`          The ID of the gym the user checked into.
    """

    __tablename__ = "checkin"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False)
    gym_id = Column(Integer, ForeignKey("gym.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # Make relationship with gym and user
    gym = relationship("Gym", back_populates="checkins")
    user = relationship("User", back_populates="checkins")
