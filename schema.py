from graphene import ObjectType, String, ID, List
from graphene.types.datetime import DateTime

class GymType(ObjectType):
  id = ID()
  name = String()
  hours = String()

class Query(ObjectType):
  hello = String(name=String(required=True))
  gyms = List(String, now=DateTime())

  def resolve_hello(self, info, name):
    return 'Hello %s!' % name

  @staticmethod
  def check_gym_open(now, gym):
    for (weekday, open_time, close_time) in gym['times']:
      if weekday == now.weekday() and now.time() > open_time and now.time() < close_time:
        return True
    return False

  def resolve_gyms(self, info, now=None):
    gyms = []

    for gym_id, gym in info.context['gyms'].items():
      if now is None or Query.check_gym_open(now, gym):
        gyms.append(gym['name'])
          
    return gyms
