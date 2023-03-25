from models.gym import Gym as GymModel
import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType

class Gym(SQLAlchemyObjectType):
    class Meta:
        model = GymModel
        interfaces = (relay.Node,)

class Query(graphene.ObjectType):
    node = relay.Node.Field()
    # allowing single column sorting

    gyms = graphene.List(lambda: Gym, name=graphene.String(), description=graphene.String(), image_url=graphene.String())

    def resolve_gyms(self, info, name=None):
      query = Gym.get_query(info)
      if name:
        query=query.filter(GymModel.name == name)
      return query.all()

schema = graphene.Schema(query=Query)
