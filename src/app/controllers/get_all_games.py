from . import *

class GetAllGamesController(AppDevController):
    def get_path(self):
        return "/games/"

    def get_methods(self):
        return ["GET"]

    def content(self, **kwargs):
        games = game_dao.get_all_games()
        data = [game_dao.serialize_game(g) for g in games]
        return utils.success_response(data)
