from . import *
from datetime import datetime as dt


class GetGamesByUserController(AppDevController):
    def get_path(self):
        return "/get_games_by_user/<user_id>/"

    def get_methods(self):
        return ["GET"]

    def content(self, **kwargs):
        user_id = request.view_args["user_id"]
        user = users_dao.get_user_by_id(user_id)

        serialized_games = [game_dao.serialize_game(game) for game in user.games]
        result = {"my_games": [], "joined_games": [], "past_games": []}
        for game in serialized_games:
            game_time = utils.parse_datetime(game["time"])
            tz_info = game_time.tzinfo
            if game_time < dt.now(tz=tz_info):
                result["past_games"].append(game)
            else:
                creator_id = game["players"][0]
                if int(creator_id) == int(user_id):
                    result["my_games"].append(game)
                else:
                    result["joined_games"].append(game)

        return utils.success_response(result)
