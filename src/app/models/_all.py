from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields

from src.app.models.game import *
from src.app.models.post import *
from src.app.models.reply import *
from src.app.models.routine import *
from src.app.models.social_media import *
from src.app.models.user import *


class GameSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Game


class PostSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Post


class ReplySchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Reply


class RoutineSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Routine


class SocialMediaSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = SocialMedia


class UserSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = User
        exclude = ("created_at", "updated_at")


# Serializers
game_schema = GameSchema()
post_schema = PostSchema()
reply_schema = ReplySchema()
routine_schema = RoutineSchema()
social_media_schema = SocialMediaSchema()
user_schema = UserSchema()
