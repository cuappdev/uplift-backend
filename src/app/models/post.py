from . import *


class Post(Base):
  __tablename__ = "posts"

  id = db.Column(db.Integer, primary_key=True)
  biography = db.Column(db.String(300), nullable=False)
  expertises = db.Column(db.String(200), nullable=False)
  large_picture = db.Column(db.String(200), nullable=False)
  name = db.Column(db.String(100), nullable=False)
  quote = db.Column(db.String(100), nullable=False)
  small_picture = db.Column(db.String(200), nullable=False)
  social_media = db.relationship('SocialMedia', backref='posts')
  suggested_routines = db.relationship('Routine', backref='posts')
  summary = db.Column(db.String(300), nullable=False)

  def __init__(self, **kwargs):
    self.biography = kwargs.get('biography', '')
    self.expertises = kwargs.get('expertises', '')
    self.large_picture = kwargs.get('large_picture', '')
    self.name = kwargs.get('name', '')
    self.quote = kwargs.get('quote', '')
    self.small_picture = kwargs.get('small_picture', '')
    self.summary = kwargs.get('summary', '')

  def serialize(self):
    return {
      'id': self.id,
      'biography': self.biography,
      'expertises': self.expertises,
      'large_picture': self.large_picture,
      'name': self.name,
      'small_picture': self.small_picture,
      'summary': self.summary
    }
