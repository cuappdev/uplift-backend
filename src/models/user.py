from sqlalchemy import Column, Integer, String, ARRAY, Enum, ForeignKey
from sqlalchemy.orm import relationship
from src.database import Base
from src.models.enums import DayOfWeekEnum
from src.models.friends import Friendship

class User(Base):
    """
    An uplift user.

    Attributes:
        - `id`                                    The ID of user.
        - `email`                                 The user's email address.
        - `giveaways`                             (nullable) The list of giveaways a user is entered into.
        - `net_id`                                The user's Net ID.
        - `name`                                  The user's name.
        - `workout_goal`                          The days of the week the user has set as their personal goal.
        - `active_streak`                         The number of consecutive weeks the user has met their personal goal.
        - `max_streak`                            The maximum number of consecutive weeks the user has met their personal goal.
        - `workout_goal`                          The max number of weeks the user has met their personal goal.
        - `encoded_image`                         The profile picture URL of the user.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=True)
    giveaways = relationship("Giveaway", secondary="giveaway_instance", back_populates="users")
    net_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    active_streak = Column(Integer, nullable=True)
    max_streak = Column(Integer, nullable=True)
    workout_goal = Column(ARRAY(Enum(DayOfWeekEnum)), nullable=True)
    encoded_image = Column(String, nullable=True)
    fcm_token = Column(String, nullable=False)
    workout_reminders = relationship("WorkoutReminder")

    friend_requests_sent = relationship("Friendship",
                                        foreign_keys="Friendship.user_id",
                                        back_populates="user")

    friend_requests_received = relationship("Friendship",
                                            foreign_keys="Friendship.friend_id",
                                            back_populates="friend")

    def add_friend(self, friend):
        # Check if friendship already exists
        existing = Friendship.query.filter(
            (Friendship.user_id == self.id) &
            (Friendship.friend_id == friend.id)
        ).first()

        if not existing:
            new_friendship = Friendship(user_id=self.id, friend_id=friend.id)
            # Add to database session here or return for external handling
            return new_friendship

    def remove_friend(self, friend):
        friendship = Friendship.query.filter(
            (Friendship.user_id == self.id) &
            (Friendship.friend_id == friend.id)
        ).first()

        if friendship:
            # Delete from database session here or return for external handling
            return friendship

    def get_friends(self):
        # Get users this user has added as friends
        direct_friends_query = Friendship.query.filter_by(user_id=self.id)
        direct_friends = [friendship.friend for friendship in direct_friends_query]

        # Get users who have added this user as a friend
        reverse_friends_query = Friendship.query.filter_by(friend_id=self.id)
        reverse_friends = [friendship.user for friendship in reverse_friends_query]

        # Combine both lists and remove duplicates
        all_friends = list(set(direct_friends + reverse_friends))

        return all_friends
