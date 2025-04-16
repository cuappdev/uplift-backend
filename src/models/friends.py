from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from src.database import Base
from datetime import datetime

class Friendship(Base):
    """
    A friendship relationship between two users.

    Attributes:
        - `id`                 The ID of the friendship.
        - `user_id`            The ID of the user who initiated the friendship.
        - `friend_id`          The ID of the user who received the friendship request.
        - `created_at`         When the friendship was created.
        - `is_accepted`        Whether the friendship has been accepted.
        - `accepted_at`        When the friendship was accepted.
    """

    __tablename__ = "friends"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    friend_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    __table_args__ = (UniqueConstraint('user_id', 'friend_id', name='unique_friendship'),)

    created_at = Column(DateTime, default=datetime.utcnow)
    is_accepted = Column(Boolean, default=False)
    accepted_at = Column(DateTime, nullable=True)

    user = relationship("User", foreign_keys=[user_id], back_populates="friend_requests_sent")
    friend = relationship("User", foreign_keys=[friend_id], back_populates="friend_requests_received")

    def accept(self):
        """Accept a friendship request."""
        self.is_accepted = True
        self.accepted_at = datetime.utcnow()
