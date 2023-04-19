import datetime as dt 

from graphene import Field, ObjectType, String, List, Int, Boolean
from graphene.types.datetime import Date, Time

from models.gym import Gym as GymModel, GymTime as GymTimeModel
from models.daytime import DayTime as DayTimeModel
from models.capacity import Capacity as CapacityModel
import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType
from sqlalchemy import desc


class Gym(SQLAlchemyObjectType):
    class Meta:
        model = GymModel
        interfaces = (relay.Node,)

    times = graphene.List(lambda: DayTime, day=graphene.Int(), start_time=graphene.DateTime(), end_time=graphene.DateTime(), restrictions=graphene.String(), special_hours=graphene.Boolean())
    capacities = graphene.List(lambda: Capacity, gym_id=graphene.Int())

    @staticmethod
    def resolve_times(self, info, day=None, start_time=None, end_time=None):
        query = GymTime.get_query(info=info)
        query = query.filter(GymTimeModel.gym_id == self.id)
        query_daytime = DayTime.get_query(info=info) #could be wrong
        if day:
          query_daytime = query_daytime.filter(DayTimeModel.day == day)
        if start_time:
          query_daytime = query_daytime.filter(DayTimeModel.start_time == start_time)
        if end_time:
          query_daytime = query_daytime.filter(DayTimeModel.end_time == end_time)
        
        daytime_queries = []
        for row in query:
          daytime = query_daytime.filter(DayTimeModel.id == row.daytime_id)
          if daytime.first():
            daytime_queries.append(daytime[0])

        return daytime_queries

    @staticmethod
    def resolve_capacities(self, info, gym_id = None):
      query = Capacity.get_query(info=info) \
        .filter(CapacityModel.gym_id == self.id) \
        .order_by(desc(CapacityModel.updated))

      return [query.first()]
        
class DayTime(SQLAlchemyObjectType):
  class Meta:
    model = DayTimeModel
    interfaces = (relay.Node,)

class GymTime(SQLAlchemyObjectType):
  class Meta:
    model = GymTimeModel
    interfaces = (relay.Node,)

class Capacity(SQLAlchemyObjectType):
  class Meta:
    model = CapacityModel
  

class Query(graphene.ObjectType):
    node = relay.Node.Field()
    # allowing single column sorting

    gyms = graphene.List(lambda: Gym, 
      id=graphene.Int(),
      name=graphene.String(), 
      description=graphene.String(), 
      location=graphene.String(),
      latitude=graphene.Float(),
      longitude=graphene.Float(),
      image_url=graphene.String())

    def resolve_gyms(self, info, name=None):
      query = Gym.get_query(info)
      if name:
        query=query.filter(GymModel.name == name)
      return query.all()

schema = graphene.Schema(query=Query)
