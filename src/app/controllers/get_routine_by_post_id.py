from . import *

class GetRoutineByPostIdController(AppDevController):

  def get_path(self):
    return '/routine/<post_id>/'

  def get_methods(self):
    return ['GET']

  def content(self, **kwargs):
    routine = routine_dao.get_routine_by_post_id(request.view_args['post_id'])
    return routine_dao.serialize_routine(routine)