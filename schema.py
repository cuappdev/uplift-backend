from graphene import Field, ObjectType, String, List, Int, Float, Boolean
from graphene.types.datetime import DateTime, Time

class Data(object):
  gyms = {}
  classes = {}
  class_details = {}

  @staticmethod
  def update_data(**kwargs):
    Data.gyms = kwargs.get('gyms')
    Data.classes = kwargs.get('classes')
    Data.class_details = kwargs.get('class_details')

class DayTimeRangeType(ObjectType):
  day = Int(required=True)
  start_time = Time(required=True)
  end_time = Time(required=True)

class GymType(ObjectType):
  id = String(required=True)
  name = String(required=True)
  description = String(required=True)
  popular = List(List(Int))
  times = List(DayTimeRangeType, required=True)
  image_url = String()

  def is_open(self, now=None):
    if now is None:
      return True
    for dt_range in self.times:
      if (now.weekday() == dt_range.day
              and dt_range.start_time <= now.time() <= dt_range.end_time):
        return True
    return False

class TagType(ObjectType):
  label = String(required=True)
  image_url = String(required=True)

class ClassDetailType(ObjectType):
  id = String(required=True)
  name = String(required=True)
  description = String(required=True)
  tags = List(TagType, required=True)
  categories = List(String, required=True)

class ClassType(ObjectType):
  id = String(required=True)
  gym_id = String()
  gym = Field(GymType)
  location = String(required=True)
  details_id = String(required=True)
  details = Field(ClassDetailType, required=True)
  start_time = DateTime()
  end_time = DateTime()
  instructor = String(required=True)
  is_cancelled = Boolean(required=True)

  def resolve_gym(self, info):
    return Data.gyms.get(self.gym_id)

  def resolve_details(self, info):
    return Data.class_details.get(self.details_id)

  def filter(self, now=None, name=None, tags=None, gym_id=None, instructor=None):
    details = Data.class_details.get(self.details_id)
    return (
        (now is None or now.date() == self.start_time.date())
        and (name is None or name in details.name)
        and (tags is None
             or any([tag in details.tags for tag in tags]))
        and (gym_id is None or gym_id == self.gym_id)
        and (instructor is None or instructor in self.instructor)
    )

class Query(ObjectType):
  gyms = List(GymType, now=DateTime(), gym_id=String(name='id'))
  classes = List(
      ClassType,
      now=DateTime(),
      name=String(),
      tags=List(String),
      gym_id=String(),
      instructor=String()
  )

  def resolve_gyms(self, info, now=None, gym_id=None):
    if gym_id is not None:
      gym = Data.gyms.get(gym_id)
      return [gym] if gym is not None else []
    return [gym for gym in Data.gyms.values() if gym.is_open(now)]

  def resolve_classes(self, info, **kwargs):
    return [c for c in Data.classes.values() if c.filter(**kwargs)]
