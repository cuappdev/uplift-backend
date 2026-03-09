from sqlalchemy import Column, Integer, String, DateTime, Boolean, text
from sqlalchemy.dialects.postgresql import JSONB
from src.database import Base
from datetime import datetime, timezone

class WeeklyChallenge(Base):
    """
    A weekly challenge.

    Attributes:
        - `id`              The ID of weekly challenge.
        - `title`           The title of weekly challenge.
        - `description`     The challenge's description.
        - `category`        The challenge's category.
        - `points`          The amount of points rewarded for the challenge's completion.
        - `start_date`      The start date of the weekly challenge.
        - `end_date`        The end date of the weekly challenge.
        - `rule_type`       The type of rule for the challenge.
        - `rule_config`     The configuration for the challenge's rule.
        - `is_active`       Whether the challenge is active.
    """
    __tablename__ = "weekly_challenge"

    id = Column(Integer, primary_key = True, autoincrement = True)
    title = Column(String, nullable = False)
    description = Column(String, nullable = False)
    category = Column(String, nullable = False)
    points = Column(Integer, nullable = False)

    start_date = Column(DateTime(timezone=True), nullable = False)
    end_date = Column (DateTime(timezone=True), nullable = False)

    rule_type = Column(String, nullable = False)
    rule_config = Column(JSONB, nullable = True)
    is_active = Column(Boolean, nullable = False, default = True)

    created_at = Column(DateTime(timezone=True), nullable = False, default=lambda: datetime.now(timezone.utc), server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime(timezone=True), nullable = False, default=lambda: datetime.now(timezone.utc), server_default=text("CURRENT_TIMESTAMP"), onupdate=lambda: datetime.now(timezone.utc))