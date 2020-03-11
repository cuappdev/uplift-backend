from . import *


class CreateReplyController(AppDevController):
    def get_path(self):
        return "/create_reply/"

    def get_methods(self):
        return ["POST"]

    def content(self, **kwargs):
        game_id = request.form["game_id"]
        game = game_dao.get_game_by_id(game_id)
        if not game:
            return {
                "result": "fail",
                "error": "game not found"
            }
        user_id = request.form["user_id"]
        text = request.form["text"]

        _, reply = reply_dao.create_reply(
            user_id=user_id,
            game_id=game_id,
            text=text
        )

        game.replies.append(reply)
        db.session.add(reply)
        db.session.commit()
        return {
            "result": "success"
        }
