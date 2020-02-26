from . import *


class JoinGameController(AppDevController):
    def get_path(self):
        return "/join_game/"

    def get_methods(self):
        return ["POST"]

    def content(self, **kwargs):
        user_id = request.form["user_id"]
        game_id = request.form["game_id"]

        game = game_dao.get_game_by_id(game_id)
        