from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, DateTime, Enum, Boolean, ForeignKey, UniqueConstraint
from src.database import Base
from src.models.enums import UserWeeklyChallengeStatus

class UserWeeklyChallenges(Base):
    """
    A user's weekly challenges.

    Attributes:
        - `id`              The ID of user's weekly challenges.
        - `user_id`         The ID of the user who owns the weekly challenges.
        - `weekly_challenge_id` The ID of the weekly challenge.
    """
    __tablename__ = "user_weekly_challenges"

    id = Column(Integer, primary_key = True, autoincrement = True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    weekly_challenge_id = Column(Integer, ForeignKey("weekly_challenge.id", ondelete="CASCADE"), nullable=False)

    completed_at = Column(DateTime(timezone=True), nullable=True)
    points = Column(Integer, nullable=False)
    status = Column(Enum(UserWeeklyChallengeStatus), nullable=False, default=UserWeeklyChallengeStatus.NOT_STARTED)
    is_completed = Column(Boolean, nullable=False, default=False)

    __table_args__ = (UniqueConstraint('user_id', 'weekly_challenge_id', name='unique_user_weekly_challenge'),)