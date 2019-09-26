from functools import wraps
from flask import request
from src.app.dao import users_dao


def auth_bearer(f):
    @wraps(f)
    def inner(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if auth_header is None:
            raise Exception("Missing authorization header.")

        bearer_token = auth_header.replace("Bearer ", "").strip()
        if bearer_token is None or not bearer_token:
            raise Exception("Invalid authorization header.")

        return f(bearer_token=bearer_token, *args, **kwargs)

    return inner


def authorize_user(f):
    @wraps(f)
    @auth_bearer
    def inner(*args, **kwargs):
        session_token = kwargs.get("bearer_token")
        user = users_dao.get_user_by_session_token(session_token)
        if not user or not user.verify_session_token(session_token):
            raise Exception("Invalid session token.")

        return f(user=user, *args, **kwargs)

    return inner
