from models.gym import Gym as GymModel, GymTime as GymTimeModel
from models.daytime import DayTime as DayTimeModel
import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType

class Gym(SQLAlchemyObjectType):
    class Meta:
        model = GymModel
        interfaces = (relay.Node,)

    times = graphene.List(lambda: DayTime, day=graphene.Int(), start_time=graphene.DateTime(), end_time=graphene.DateTime(), restrictions=graphene.String(), special_hours=graphene.Boolean())

    def resolve_times(self, info, day=None):
        query = GymTime.get_query(info=info)
        query = query.filter(GymTimeModel.gym_id == self.id)
        query_daytime = DayTime.get_query(info=info) #could be wrong
        daytime_queries = []
        for row in query:
          query_daytime = query_daytime.filter(DayTimeModel.id == row.daytime_id)
          daytime_queries.append(query_daytime[0])

        return daytime_queries




class DayTime(SQLAlchemyObjectType):
  class Meta:
    model = DayTimeModel
    interfaces = (relay.Node,)


  

class GymTime(SQLAlchemyObjectType):
  class Meta:
    model = GymTimeModel
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
