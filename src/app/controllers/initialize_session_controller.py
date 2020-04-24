import os
from . import *
from google.auth.transport import requests
from google.oauth2 import id_token

CLIENT_ID = os.environ["CLIENT_ID"]


class InitializeSessionController(AppDevController):
    def get_path(self):
        return "/login/"

    def get_methods(self):
        return ["POST"]

    def content(self, **kwargs):
        token = request.form.get("token")
        try:
            id_info = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)

            if id_info["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
                raise ValueError("Wrong issuer.")

            # ID token is valid. Get the user's Google Account information.
            created, user = users_dao.create_user(id_info)
            data = {
                "session_token": user.session_token,
                "session_expiration": user.session_expiration,
                "update_token": user.update_token,
            }
            return utils.success_response(data)

        except ValueError:
            return utils.failure_response("Invalid token")
