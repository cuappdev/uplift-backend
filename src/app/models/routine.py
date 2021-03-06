from . import *


class Routine(Base):
    __tablename__ = "routines"

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)
    steps = db.Column(db.String(1500), nullable=False)
    title = db.Column(db.String(200), nullable=False)

    def __init__(self, **kwargs):
        self.category = kwargs.get("category", "")
        self.post_id = kwargs.get("post_id", 0)
        self.steps = kwargs.get("steps", "")
        self.title = kwargs.get("title", "")

    def serialize(self):
        return {"id": self.id, "category": self.category, "steps": self.steps, "title": self.title}
