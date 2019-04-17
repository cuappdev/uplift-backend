import app.dao.routine_dao as rd
import app.dao.social_media_dao as smd

from . import *

def get_all_posts():
  return Post.query.all()

def get_post_by_id(post_id):
  return Post.query.filter(Post.id == post_id).first()

def get_posts_by_name(name):
  return Post.query.filter(Post.name == name).all()

def get_posts_by_routines(routines_id):
  return Post.query.filter(
    Post.routines_id == routines_id
  ).all()

def get_posts_by_social_media(social_media_id):
  return Post.query.filter(
    Post.social_media_id == social_media_id
  ).all()

def serialize_post(post):
  serialized_post = {'id': post.id}

  if post.routines_id is not None:
    serialized_post['routines_id'] = post.routines_id
  
  if post.social_media_id is not None:
    serialized_post['social_media_id'] = post.social_media_id

  return serialized_post

def create_post(args):
  biography = args.get('biography')
  category = args.get('category', '')
  expertises = args.get('expertises', '')
  facebook = args.get('facebook', '')
  instagram = args.get('instagram', '')
  large_picture = args.get('large_picture')
  linkedin = args.get('linkedin', '')
  name = args.get('name')
  quote = args.get('quote', '')
  small_picture = args.get('small_picture')
  steps = args.get('steps', '')
  summary = args.get('summary')
  title = args.get('title', '')
  twitter = args.get('twitter', '')
  website = args.get('website', '')

  _, routines = rd.create_routine(category, steps, title)
  _, social_media = smd.create_social_media(facebook, instagram, linkedin, 
    twitter, website)

  new_post = Post(
    biography=biography, 
    expertises=expertises,
    large_picture=large_picture, 
    name=name, 
    quote=quote,
    routines_id = routines.id,
    small_picture=small_picture, 
    social_media_id = social_media.id,
    summary=summary)
  db_utils.commit_model(new_post)
  return True, new_post