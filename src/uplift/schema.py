import datetime as dt 

from graphene import Field, ObjectType, String, List, Int, Boolean
from graphene.types.datetime import Date, Time

from models.gym import Gym as GymModel, GymTime as GymTimeModel
from models.daytime import DayTime as DayTimeModel
from models.activity import Activity as ActivityModel, Price as PriceModel
from models.capacity import Capacity as CapacityModel
from models.activity import Amenity as AmenityModel
import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType
from sqlalchemy import desc


class Gym(SQLAlchemyObjectType):
    class Meta:
        model = GymModel

    times = graphene.List(lambda: DayTime, day=graphene.Int(), start_time=graphene.DateTime(), end_time=graphene.DateTime(), restrictions=graphene.String(), special_hours=graphene.Boolean())
    activities = graphene.List(lambda: Activity, name=graphene.String())
<<<<<<< HEAD:src/uplift/schema.py
    capacities = graphene.List(lambda: Capacity, gym_id=graphene.Int())
=======
>>>>>>> c57727e41f59b589dd6e571aedf3c9fd33217700:src/app2/schema.py

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
            if activity.first() and (name == act.name or name == None):
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
    prices = graphene.List(lambda: Price, cost=graphene.Int(), one_time=graphene.Boolean())

    def resolve_gyms(self, info, name=None):
        query = Gym.get_query(info=info)
        gym_queries = []
        for g in self.gyms:
            gym = query.filter(GymModel.id == g.id)
            if gym.first() and (name == g.name or name == None):
                gym_queries.append(gym[0])
              
        return gym_queries

<<<<<<< HEAD:src/uplift/schema.py
=======
class Capacity(SQLAlchemyObjectType):
  class Meta:
    model = CapacityModel
  
>>>>>>> master:src/uplift/schema.py
=======
    def resolve_prices(self, info, cost=None, one_time=None):
      query = Price.get_query(info=info)
      query = query.filter(PriceModel.activity_id == self.id)
      if cost:
        query = query.filter(PriceModel.cost == cost)
      if one_time is not None:
        query = query.filter(PriceModel.one_time == one_time)
      return query

class Price(SQLAlchemyObjectType):
  class Meta:
    model = PriceModel

class Amenity(SQLAlchemyObjectType):
  class Meta:
    model = AmenityModel

>>>>>>> c57727e41f59b589dd6e571aedf3c9fd33217700:src/app2/schema.py

class Query(graphene.ObjectType):

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

    activities = graphene.List(lambda: Activity, name=graphene.String( \
      ), details=graphene.String(), image_url=graphene.String())

    def resolve_activities(self, info, name=None):
        query = Activity.get_query(info)
        if name:
            query = query.filter(ActivityModel.name == name)
        return query.all()

schema = graphene.Schema(query=Query)
