from . import *

class GetAllRoutinesController(AppDevController):

  def get_path(self):
    return '/routines/'

  def get_methods(self):
    return ['GET']

  def content(self, **kwargs):
    routines = routine_dao.get_all_routines()
    return [routine_dao.serialize_routine(routine) for routine in routines]