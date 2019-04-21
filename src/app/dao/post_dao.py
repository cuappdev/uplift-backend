import src.app.dao.routine_dao as rd
import src.app.dao.social_media_dao as smd

from . import *

def get_all_posts():
  return Post.query.all()

def get_post_by_id(post_id):
  return Post.query.filter(Post.id == post_id).first()

def get_posts_by_name(name):
  return Post.query.filter(Post.name == name).all()

def serialize_post(post):
  return post_schema.dump(post).data

def create_post(args):
  biography = args.get('biography')
  college = args.get('college')
  expertises = args.get('expertises', '')
  large_picture = args.get('large_picture', '')
  name = args.get('name')
  quote = args.get('quote', '')
  small_picture = args.get('small_picture', '')

  new_post = Post(
    biography=biography, 
    college=college,
    expertises=expertises,
    large_picture=large_picture, 
    name=name, 
    quote=quote,
    small_picture=small_picture
    )
  db_utils.commit_model(new_post)
  return True, new_post