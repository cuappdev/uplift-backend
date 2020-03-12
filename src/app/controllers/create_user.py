from . import *

"""
Controller used for testing, will delete later
"""
class CreateUserController(AppDevController):
    def get_path(self):
        return "/create_user/"

    def get_methods(self):
        return ["POST"]

    def content(self, **kwargs):
        sub = request.form["sub"]
        email = request.form["email"]
        _, user = users_dao.create_user({
            "sub": sub,
            "email": email,
            "given_name": "test",
            "name": "test",
            "picture": "test"
        })
        return {"result": "success"}
