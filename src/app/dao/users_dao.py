from . import *


def get_user_by_google_id(google_id):
    return User.query.filter(User.google_id == google_id).first()


def get_user_by_session_token(session_token):
    return User.query.filter(User.session_token == session_token).first()


def get_user_by_update_token(update_token):
    return User.query.filter(User.update_token == update_token).first()


def create_user(id_info):
    optional_user = get_user_by_google_id(id_info["sub"])
    if optional_user is not None:
        # user with google_id exists
        return False, optional_user

    google_id = id_info["sub"]
    email = id_info["email"]
    given_name = id_info["given_name"]
    name = id_info["name"]
    picture = id_info["picture"]

    user = User(google_id=google_id, email=email, given_name=given_name, name=name, picture=picture)
    db_utils.commit_model(user)
    return True, user


def renew_session(update_token):
    user = get_user_by_update_token(update_token)

    if user is None:
        raise Exception("Invalid update token.")

    user.renew_session()
    db_utils.db_session_commit()
    return user
