import graphene
from graphene import ObjectType
from graphene_sqlalchemy import SQLAlchemyObjectType
from src.models.gym import Gym as GymModel
from src.models.activity import Activity as ActivityModel
from src.models.openhours import OpenHours as OpenHoursModel


# MARK: - Gym

class Gym(SQLAlchemyObjectType):
  class Meta:
    model = GymModel

  activities = graphene.List(lambda: Activity, name=graphene.String())

  def resolve_activities(self, info, name=None):
    query = Activity.get_query(info=info).filter(ActivityModel.gym_id == self.id)
    return query


# MARK: - Activity

class Activity(SQLAlchemyObjectType):
  class Meta:
      model = ActivityModel

  open_hours = graphene.List(lambda: OpenHours, name=graphene.String())

  def resolve_open_hours(self, info, name=None):
    query = OpenHours.get_query(info=info).filter(OpenHoursModel.activity_id == self.id)
    return query


# MARK: - Open Hours

class OpenHours(SQLAlchemyObjectType):
  class Meta:
    model = OpenHoursModel


# MARK: - Query

class Query(graphene.ObjectType):
  gyms = graphene.List(Gym)

  def resolve_gyms(self, info, name=None):
    query = Gym.get_query(info)
    return query.all()


schema = graphene.Schema(query=Query)
