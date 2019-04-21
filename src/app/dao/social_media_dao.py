from . import *

def get_all_social_media():
  return SocialMedia.query.all()

def get_social_media_by_id(social_media_id):
  return SocialMedia.query.filter(SocialMedia.id == social_media_id).first()

def get_social_media_by_post_id(post_id):
  return SocialMedia.query.filter(SocialMedia.post_id == post_id).all()

def serialize_social_media(social_media):
  return social_media_schema.dump(social_media).data

def create_social_media(facebook="", instagram="", linkedin="", post_id, twitter="", website=""):
  new_social_media = SocialMedia(
    facebook=facebook, 
    instagram=instagram, 
    linkedin=linkedin,
    post_id=post_id,
    twitter=twitter, 
    website=website)
  db_utils.commit_model(new_social_media)
  return True, new_social_media