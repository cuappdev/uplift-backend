from . import *
from datetime import datetime

class User(Base):
  __tablename__ = "users"

  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(100), unique=True, nullable=False)
  name = db.Column(db.String(100), nullable=True)
  avatar = db.Column(db.String(200))
  active = db.Column(db.Boolean, default=False)
  tokens = db.Column(db.Text) # Stores the access and refresh tokens JSON from Google
  created_at = db.Column(db.DateTime, default=datetime.utcnow())

  def __init__(self, **kwargs):
    # TODO: Implement this
    pass