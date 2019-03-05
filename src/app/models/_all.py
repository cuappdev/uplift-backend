from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields

from src.app.models.user import *

class UserSchema(ModelSchema):
  class Meta(ModelSchema.Meta):
    model = User
    exclude = ('created_at', 'updated_at')

# Serializers
user_schema = UserSchema()