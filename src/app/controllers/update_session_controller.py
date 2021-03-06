from . import *


class UpdateSessionController(AppDevController):
    def get_path(self):
        return "/session/"

    def get_methods(self):
        return ["POST"]

    @auth_bearer
    def content(self, **kwargs):
        update_token = kwargs.get("bearer_token")

        if update_token is None:
            return utils.failure_response("Invalid update token")

        user = users_dao.renew_session(update_token)
        data = {
            "session_token": user.session_token,
            "session_expiration": user.session_expiration,
            "update_token": user.update_token,
        }
        return utils.success_response(data)
