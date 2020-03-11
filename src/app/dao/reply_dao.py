from . import *


def get_reply_by_id(reply_id):
    return Reply.query.filter(Reply.id == reply_id).first()

def create_reply(**kwargs):
    new_reply = Reply(
        user_id=kwargs.get("user_id"),
        game_id=kwargs.get("game_id"),
        text=kwargs.get("text")
    )
    db_utils.commit_model(new_reply)
    return True, new_reply

def serialize_reply(reply):
    return reply_schema.dump(reply)
