from sqlalchemy import ARRAY, CheckConstraint, Column, Integer, ForeignKey, String, Text, DateTime, text
from sqlalchemy import Enum as SQLAEnum
from sqlalchemy.orm import relationship
from src.database import Base
from src.models.enums import MuscleGroupEnum
from src.utils.constants import WORKOUT_RATING_MAX, WORKOUT_RATING_MIN, WORKOUT_TITLE_MAX_LENGTH


class Workout(Base):
    """
    A workout logged by a user.

    A workout is created when a user checks in at a gym. Saving the workout
    afterwards adds when it started and ended, a title, notes, and a rating.

    Attributes:
        - `id`              The ID of the workout.
        - `workout_time`    The date and time of the workout (the check-in time).
        - `user_id`         The ID of the user who completed the workout.
        - `facility_id`     The ID of the facility visited
        - `started_at`      When the workout started. Null until the workout is saved.
        - `ended_at`        When the workout ended. Null until the workout is saved.
        - `title`           The user's name for the workout. Optional.
        - `description`     The user's notes about the workout. Optional.
        - `rating`          How satisfied the user was, from 0 to 5. Optional.
        - `muscle_groups`   The muscle groups the user worked. Empty until the workout is saved.
    """

    __tablename__ = "workout"
    __table_args__ = (
        CheckConstraint(
            "rating >= %d AND rating <= %d" % (WORKOUT_RATING_MIN, WORKOUT_RATING_MAX), name="ck_workout_rating_range"
        ),
    )

    id = Column(Integer, primary_key=True)
    workout_time = Column(
        DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )  # should this be nullable?
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    facility_id = Column(Integer, ForeignKey("facility.id"), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    title = Column(String(WORKOUT_TITLE_MAX_LENGTH), nullable=True)
    description = Column(Text, nullable=True)
    rating = Column(Integer, nullable=True)
    muscle_groups = Column(ARRAY(SQLAEnum(MuscleGroupEnum)), nullable=False, server_default=text("'{}'"), default=list)

    user = relationship("User", back_populates="workouts")
