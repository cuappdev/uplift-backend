import datetime
from . import *


class Comment(Base):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    text = db.Column(db.String(100000), nullable=False)
    replies = db.relationship("Reply", backref="comments")

    def __init__(self, **kwargs):
        self.user_id = kwargs.get("user_id")
        self.text = kwargs.get("text", "")
