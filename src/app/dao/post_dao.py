from . import routine_dao as rd
from . import social_media_dao as smd

from . import *


def get_all_posts():
    return Post.query.all()


def get_post_by_id(post_id):
    return Post.query.filter(Post.id == post_id).first()


def get_posts_by_name(name):
    return Post.query.filter(Post.name == name).all()


def serialize_post(post):
    return post_schema.dump(post)


def create_post(**kwargs):
    new_post = Post(
        biography=kwargs.get("biography", ""),
        college=kwargs.get("college", ""),
        expertises=kwargs.get("expertises", ""),
        large_picture=kwargs.get("large_picture", ""),
        name=kwargs.get("name", ""),
        quote=kwargs.get("quote", ""),
        small_picture=kwargs.get("small_picture", ""),
    )
    db_utils.commit_model(new_post)
    return True, new_post
