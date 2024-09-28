from sqlalchemy import Column, Integer, String, ARRAY
from sqlalchemy.orm import backref, relationship
from src.database import Base

# from src.models.classes import user_class_preference


class User(Base):
    """
    An uplift user.

    Attributes:
        - `id`                                    The ID of user.
        - `email`                                 The user's email address.
        - `giveaways`                             (nullable) The list of giveaways a user is entered into.
        - `net_id`                                The user's Net ID.
        - `name`                                  The user's name.
        - `total_workouts`                        The total number of workouts the user has completed.
        - `workout_goal`                          The number of workouts per week the user has set as their personal goal.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    giveaways = relationship("Giveaway", secondary="giveaway_instance", back_populates="users")
    net_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    total_workouts = Column(Integer, default=0)
    workout_goal = Column(ARRAY(String), nullable=True)
    # instagram = Column(String, nullable=True)
