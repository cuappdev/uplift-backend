from . import *


class GetRoutineByPostIdController(AppDevController):
    def get_path(self):
        return "/routine_by_post/<post_id>/"

    def get_methods(self):
        return ["GET"]

    def content(self, **kwargs):
        routines = routine_dao.get_routines_by_post_id(request.view_args["post_id"])
        return [routine_dao.serialize_routine(routine) for routine in routines]
