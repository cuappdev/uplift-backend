import datetime
import hashlib
import os
from . import *

class User(Base):
  __tablename__ = "users"

  id = db.Column(db.Integer, primary_key=True)
  google_id = db.Column(db.String(200), unique=True, nullable=False)
  email = db.Column(db.String(100), unique=True, nullable=False)
  given_name = db.Column(db.String(100), nullable=True)
  name = db.Column(db.String(100), nullable=True)
  picture = db.Column(db.String(200))
  session_token = db.Column(db.String(255), nullable=False, unique=True)
  session_expiration = db.Column(db.DateTime, nullable=False)
  update_token = db.Column(db.String(255), nullable=False, unique=True)
  created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())

  def __init__(self, **kwargs):
    self.google_id = kwargs.get('google_id')
    self.given_name = kwargs.get('given_name')
    self.name = kwargs.get('name')
    self.email = kwargs.get('email')
    self.picture = kwargs.get('picture')
    self.renew_session()

  def _urlsafe_base_64(self):
    return hashlib.sha1(os.urandom(64)).hexdigest()

  def renew_session(self):
    self.session_token = self._urlsafe_base_64()
    self.session_expiration = datetime.datetime.now() + \
                              datetime.timedelta(days=1)
    self.update_token = self._urlsafe_base_64()
