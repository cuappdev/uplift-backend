from . import *


class GetGamesByUserController(AppDevController):
    def get_path(self):
        return "/get_games_by_user/"

    def get_methods(self):
        return ["GET"]

    def content(self, **kwargs):
        user_id = request.view_args["user_id"]
        user = users_dao.get_user_by_id(user_id)

        serialized_games = [game_dao.serialize_game(game) for game in user.games]
        return serialized_games
