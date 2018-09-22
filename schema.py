from datetime import datetime, time, timedelta
from graphene import Field, ObjectType, String, List, Int, ID, Boolean
from graphene.types import Scalar
from graphene.types.datetime import DateTime, Time
from graphql.language.ast import StringValue

gyms = {}
classes = {}
class_details = {}

class DayTimeRangeType(ObjectType):
  day = Int()
  start_time = Time()
  end_time = Time()

  def __init__(self, day, start_time, end_time):
      self.day = day
      self.start_time = start_time
      self.end_time = end_time

class GymType(ObjectType):
  id = String()
  name = String()
  description = String()
  popular = List(List(Int))
  times = List(DayTimeRangeType)

  def __init__(self, name, description, popular, times):
      self.name = name
      self.description = description
      self.popular = popular
      self.times = times

  def is_open(self, now=None):
    if now is None:
      return True
    for dt_range in self.times:
      print(dt_range.day, dt_range.start_time, dt_range.end_time, now.weekday(), now.time())
      if (now.weekday() == dt_range.day
              and now.time() >= dt_range.start_time
              and now.time() <= dt_range.end_time):
        return True
    return False

class ClassDetailType(ObjectType):
  id = String()
  name = String()
  description = String()
  tags = List(String)

class ClassType(ObjectType):
  id = String()
  gym_id = String()
  gym = Field(GymType)
  details_id = String()
  details = Field(ClassDetailType)
  start_time = DateTime()
  end_time = DateTime()
  instructor = String()
  is_cancelled = Boolean()

  def resolve_gym(self, info):
    return gyms.get(self.gym_id)

  def resolve_details(self, info):
    return class_details.get(self.details_id)

  def filter(self, now=None, tags=None, gym_id=None, instructor=None):
    details = class_details.get(self.details_id)
    return (
        (now is None or now.date() == self.start_time.date())
        and (tags is None
             or any([tag in details.tags for tag in tags]))
        and (gym_id is None or gym_id == self.gym_id)
        and (instructor is None or instructor == self.instructor)
    )

class Query(ObjectType):
  gyms = List(GymType, now=DateTime(), gym_id=Int(name='id'))
  classes = List(
      ClassType,
      now=DateTime(),
      tags=List(String),
      gym_id=Int(),
      instructor=String()
  )

  def resolve_gyms(self, info, now=None, gym_id=None):
    if gym_id is not None:
      gym = gyms.get(gym_id)
      return [gym] if gym is not None else []
    return [gym for gym in gyms.values() if gym.is_open(now)]

  def resolve_classes(self, info, **kwargs):
    return [c for c in classes.values() if c.filter(**kwargs)]

def init_data():
  global gyms, class_details, classes
  gyms = {
      0: GymType(
          id=0, name='Helen Newman', description='hnh description',
          popular=[
              [0,0,0,0,0,0,0,0,0,0,19,31,32,23,26,43,59,57,51,51,47,34,17,3],
              [0,0,0,0,0,0,15,25,27,22,21,31,47,53,45,34,36,52,70,75,60,35,14,0]
          ],
          times=[
              DayTimeRangeType(
                  day=0,
                  start_time=time(hour=6),
                  end_time=time(hour=23, minute=30)
              ),
              DayTimeRangeType(
                  day=6,
                  start_time=time(hour=10),
                  end_time=time(hour=23, minute=30)
              )
          ]
      )
  }

  class_details = {
      0: ClassDetailType(
          id=0, name='class name', description='class description',
          tags=['tag1', 'tag2']
      )
  }

  classes = {
      0: ClassType(
          id=0, gym_id=0, details_id=0,
          start_time=datetime.now(),
          end_time=datetime.now() + timedelta(hours=1),
          instructor='instructor',
          is_cancelled=False
      )
  }

init_data()
