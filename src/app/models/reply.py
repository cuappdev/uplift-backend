import datetime
from . import *


class Reply(Base):
    __tablename__ = "replies"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey("comments.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    text = db.Column(db.String(100000), nullable=False)

    def __init__(self, **kwargs):
        self.user_id = kwargs.get("user_id")
        self.comment_id = kwargs.get("comment_id")
        self.text = kwargs.get("text", "")
