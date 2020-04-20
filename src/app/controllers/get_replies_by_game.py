from . import *


class GetRepliesByGame(AppDevController):
    def get_path(self):
        return "/get_replies/<game_id>/"

    def get_methods(self):
        return ["GET"]

    def content(self, **kwargs):
        game_id = request.view_args["game_id"]
        game = game_dao.get_game_by_id(game_id)
        if not game:
            return {"result": "fail", "error": "game not found"}

        result = [reply_dao.serialize_reply(reply) for reply in game.replies]
        return utils.success_response(result)
