from graphene import InputObjectType, ObjectType, String, List, Int, InputField
from graphene.types.datetime import DateTime
import utils

class GymType(ObjectType):
  id = Int()
  name = String()
  description = String()
  popular = List(List(Int))

  def __init__(self, gym):
    self.id = gym['id']
    self.name = gym['name']
    self.description = gym['description']
    self.popular = gym['popular']

class ClassType(ObjectType):
  name = String()
  gym_id = Int()
  description = String()
  start_time = DateTime()
  end_time = DateTime()
  instructor = String()
  tags = List(String)

  def __init__(self, class_data, class_details_data):
    self.instructor = class_data['instructor']
    self.gym_id = class_data['gym_id']
    self.description = class_details_data['description']
    self.name = class_details_data['name']
    self.tags = class_details_data['tags']
    self.start_time = class_data['start_time']
    self.end_time = class_data['end_time']

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
    gyms_data = info.context['gyms']

    if gym_id is not None:
      if gym_id in gyms_data:
        return [GymType(gyms_data[gym_id])]
      return None

    gyms = []

    for gym_id, gym_data in gyms_data.items():
      if now is None or utils.is_gym_open(now, gym_data):
        gyms.append(GymType(gym_data))

    return gyms

  def resolve_classes(self, info,
                      now=None, tags=None,
                      gym_id=None, instructor=None):
    classes_data = info.context['classes']
    class_details_data = info.context['class_details']
    classes = []

    for class_id, class_data in classes_data.items():
      class_detail_data = class_details_data[class_data['class_description_id']]

      if ((now is None or now.date() == class_data['start_time'].date()) \
          and (tags is None \
              or any([tag in class_detail_data['tags'] for tag in tags])) \
          and (gym_id is None or gym_id == class_data['gym_id'])
          and (instructor is None or instructor == class_data['instructor'])):
        classes.append(ClassType(class_data, class_detail_data))

    return classes
