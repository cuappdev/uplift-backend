from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields

from src.app.models.post import *
from src.app.models.routine import *
from src.app.models.social_media import *
from src.app.models.user import *


class PostSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Post


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
post_schema = PostSchema()
routine_schema = RoutineSchema()
social_media_schema = SocialMediaSchema()
user_schema = UserSchema()
