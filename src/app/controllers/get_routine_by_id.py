from . import *


class GetRoutineByIdController(AppDevController):
    def get_path(self):
        return "/routine/<routine_id>/"

    def get_methods(self):
        return ["GET"]

    def content(self, **kwargs):
        routine = routine_dao.get_routine_by_id(request.view_args["routine_id"])
        return routine_dao.serialize_routine(routine)
