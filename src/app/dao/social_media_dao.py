from . import *

def get_all_social_media():
  return SocialMedia.query.all()

def get_social_media_by_id(social_media_id):
  return SocialMedia.query.filter(SocialMedia.id == social_media_id).first()

def get_social_media_by_post_id(post_id):
  return SocialMedia.query.filter(SocialMedia.post_id == post_id).all()

def serialize_social_media(social_media):
  return social_media_schema.dump(social_media).data

def create_social_media(**kwargs):
  new_social_media = SocialMedia(
    facebook=kwargs.get('facebook', ''), 
    instagram=kwargs.get('instagram', ''), 
    linkedin=kwargs.get('linkedin', ''),
    post_id=kwargs.get('post_id', 0),
    twitter=kwargs.get('twitter', ''), 
    website=kwargs.get('website', ''))
  db_utils.commit_model(new_social_media)
  return True, new_social_media