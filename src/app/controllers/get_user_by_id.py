from . import *


class GetUserByIDController(AppDevController):
    def get_path(self):
        return "/get_user_by_id/<user_id>/"

    def get_methods(self):
        return ["GET"]

    def content(self, **kwargs):
        user_id = request.view_args["user_id"]
        user = users_dao.get_user_by_id(user_id)
        return users_dao.serialize_user(user)
