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

    all_gyms = SQLAlchemyConnectionField(Gym.connection, sort=Gym.sort_argument())
    # Allows sorting over mutliple columns, by default over primary key

schema = graphene.Schema(query=Query)
