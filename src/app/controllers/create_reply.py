from . import *


class CreateReplyController(AppDevController):
    def get_path(self):
        return "/create_reply/"

    def get_methods(self):
        return ["POST"]

    def content(self, **kwargs):
        game_id = request.form.get("game_id")
        game = game_dao.get_game_by_id(game_id)
        if not game:
            return utils.failure_response("Game not found")
        user_id = request.form.get("user_id")
        text = request.form.get("text")

        _, reply = reply_dao.create_reply(user_id=user_id, game_id=game_id, text=text)

        game.replies.append(reply)
        db.session.add(reply)
        db.session.commit()
        

        return utils.success_response(game_dao.serialize_game(game))
