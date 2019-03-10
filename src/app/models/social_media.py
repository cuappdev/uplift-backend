from . import *


class SocialMedia(Base):
  __tablename__ = "social_media"

  id = db.Column(db.Integer, primary_key=True)
  facebook = db.Column(db.String(200), nullable=True)
  instagram = db.Column(db.String(200), nullable=True)
  linkedin = db.Column(db.String(200), nullable=True)
  post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
  twitter = db.Column(db.String(200), nullable=True)
  website = db.Column(db.String(200), nullable=True)

  def __init__(self, **kwargs):
    self.facebook = kwargs.get('facebook', '')
    self.instagram = kwargs.get('instagram', '')
    self.linkedin = kwargs.get('linkedin', '')
    self.post_id = kwargs.get('post_id')
    self.twitter = kwargs.get('twitter', '')
    self.website = kwargs.get('website', '')

  def serialize(self):
    return {
      'id': self.id,
      'facebook': self.facebook,
      'instagram': self.instagram,
      'linkedin': self.linkedin,
      'twitter': self.twitter,
      'website': self.website
    }
