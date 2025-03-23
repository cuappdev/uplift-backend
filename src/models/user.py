from sqlalchemy import Column, Integer, String, ARRAY, Enum, Table, ForeignKey
from sqlalchemy.orm import backref, relationship
from src.database import Base
from src.models.enums import DayOfWeekEnum

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

    friendship = Table(
        "friends",
        Base.metadata,
        Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
        Column("friend_id", Integer, ForeignKey("users.id"), primary_key=True),
    )

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=True)
    giveaways = relationship("Giveaway", secondary="giveaway_instance", back_populates="users")
    net_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    active_streak = Column(Integer, nullable=True)
    max_streak = Column(Integer, nullable=True)
    workout_goal = Column(ARRAY(Enum(DayOfWeekEnum)), nullable=True)
    encoded_image = Column(String, nullable=True)

    friends = relationship(
        'User',
        secondary=friendship,
        primaryjoin=(friendship.c.user_id == id),
        secondaryjoin=(friendship.c.friend_id == id),
        backref=backref('friended_by', lazy='dynamic'),
        lazy='dynamic'
    )

    def add_friend(self, friend):
        if friend not in self.friends:
            self.friends.append(friend)

    def remove_friend(self, friend):
        if friend in self.friends:
            self.friends.remove(friend)

    def get_friends(self):
        # Get direct friends (users this user has added)
        direct_friends = self.friends.all()

        # Get users who have added this user as a friend
        reverse_friends = self.friended_by.all()

        # Combine both lists and remove duplicates using set
        all_friends = list(set(direct_friends + reverse_friends))

        return all_friends
