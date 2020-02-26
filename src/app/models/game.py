import datetime
from . import *


class Game(Base):
    __tablename__ = "games"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    text = db.Column(db.String(100000), nullable=False)
    replies = db.relationship("Reply", backref="games")
    title = db.Column(db.String(100), nullable=False)
    time = db.Column(db.DateTime)
    location = db.Column(db.String(100), nullable=False)
    max_players = db.Column(db.Integer)
    players = db.relationship("User", backref="players")

    def __init__(self, **kwargs):
        self.user_id = kwargs.get("user_id")
        self.text = kwargs.get("text", "")
        self.title = kwargs.get("title", "")
        self.time = kwargs.get("time")
        self.location = kwargs.get("location")
        self.max_players = kwargs.get("max_players")
