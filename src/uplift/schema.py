import datetime as dt 

from graphene import Field, ObjectType, String, List, Int, Boolean
from graphene.types.datetime import Date, Time

from models.gym import Gym as GymModel, GymTime as GymTimeModel
from models.daytime import DayTime as DayTimeModel
<<<<<<< HEAD:src/app2/schema.py
from models.activity import Activity as ActivityModel, Price as PriceModel
=======
from models.capacity import Capacity as CapacityModel
>>>>>>> master:src/uplift/schema.py
import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType
from sqlalchemy import desc


class Gym(SQLAlchemyObjectType):
    class Meta:
        model = GymModel
        interfaces = (relay.Node,)

    times = graphene.List(lambda: DayTime, day=graphene.Int(), start_time=graphene.DateTime(), end_time=graphene.DateTime(), restrictions=graphene.String(), special_hours=graphene.Boolean())
    activities = graphene.List(lambda: Activity, name=graphene.String())
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

<<<<<<< HEAD:src/app2/schema.py
    def resolve_activities(self, info, name=None):
        query = Activity.get_query(info=info)
        activity_queries = []
        for act in self.activities:
            activity = query.filter(ActivityModel.id == act.id)
            if activity.first():
                if name and act.name == name:
                    activity_queries.append(activity[0])
                elif not name:
                    activity_queries.append(activity[0])
        return activity_queries
=======
    @staticmethod
    def resolve_capacities(self, info, gym_id = None):
      query = Capacity.get_query(info=info) \
        .filter(CapacityModel.gym_id == self.id) \
        .order_by(desc(CapacityModel.updated))

      return [query.first()]
>>>>>>> master:src/uplift/schema.py
        
class DayTime(SQLAlchemyObjectType):
  class Meta:
    model = DayTimeModel

class GymTime(SQLAlchemyObjectType):
  class Meta:
    model = GymTimeModel

<<<<<<< HEAD:src/app2/schema.py
class Activity(SQLAlchemyObjectType):
    class Meta:
        model = ActivityModel

    gyms = graphene.List(lambda: Gym, name=graphene.String())

    def resolve_gyms(self, info, name=None):
        query = Gym.get_query(info=info)
        gym_queries = []
        for g in self.gyms:
            gym = query.filter(GymModel.id == g.id)
            if gym.first():
                if name and g.name == name:
                    gym_queries.append(gym[0])
                elif not name:
                    gym_queries.append(gym[0])
        return gym_queries

=======
class Capacity(SQLAlchemyObjectType):
  class Meta:
    model = CapacityModel
  
>>>>>>> master:src/uplift/schema.py

class Query(graphene.ObjectType):
    # node = relay.Node.Field()
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

    activities = graphene.List(lambda: Activity, name=graphene.String(
    ), details=graphene.String(), image_url=graphene.String())

    def resolve_activities(self, info, name=None):
        query = Activity.get_query(info)
        if name:
            query = query.filter(ActivityModel.name == name)
        return query.all()

schema = graphene.Schema(query=Query)
