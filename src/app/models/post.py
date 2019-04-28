from . import *


class Post(Base):
  __tablename__ = "posts"

  id = db.Column(db.Integer, primary_key=True)
  biography = db.Column(db.String(100000), nullable=False)
  college = db.Column(db.String(100), nullable=False)
  expertises = db.Column(db.String(1000), nullable=False)
  large_picture = db.Column(db.String(500), nullable=False)
  name = db.Column(db.String(100), nullable=False)
  quote = db.Column(db.String(500), nullable=False)
  routines = db.relationship('Routine', backref='posts')
  small_picture = db.Column(db.String(500), nullable=False)
  social_media = db.relationship('SocialMedia', backref='posts')

  def __init__(self, **kwargs):
    self.biography = kwargs.get('biography', '')
    self.college = kwargs.get('college', '')
    self.expertises = kwargs.get('expertises', '')
    self.large_picture = kwargs.get('large_picture', '')
    self.name = kwargs.get('name', '')
    self.quote = kwargs.get('quote', '')
    self.small_picture = kwargs.get('small_picture', '')

  def serialize(self):
    return {
      'id': self.id,
      'biography': self.biography,
      'college': self.college,
      'expertises': self.expertises,
      'large_picture': self.large_picture,
      'name': self.name,
      'small_picture': self.small_picture
    }
