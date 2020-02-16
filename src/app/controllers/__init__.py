from flask import jsonify, redirect, render_template, request
from appdev.controllers import *
from src.app.dao import game_dao, post_dao, routine_dao, social_media_dao, users_dao
from src.app.models._all import *
from src.app.utils.authorize import *

game_schema = GameSchema()
post_schema = PostSchema()
reply_schema = ReplySchema()
routine_schema = RoutineSchema()
social_media_schema = SocialMediaSchema()
user_schema = UserSchema()
