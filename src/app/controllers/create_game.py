from . import *
from datetime import datetime as dt


class CreateGameController(AppDevController):
    def get_path(self):
        return "/create_game/"

    def get_methods(self):
        return ["POST"]

    def content(self, **kwargs):
        user_id = request.form["user_id"]
        title = request.form["title"]
        text = request.form["text"]
        time = dt.strptime(request.form["time"], '%Y-%m-%d, %H:%M')
        location = request.form["location"]
        max_players = request.form["max_players"]

        game_dao.create_game(
            user_id=user_id,
            text=text,
            time=time,
            title=title,
            location=location,
            max_players=max_players,
        )

        return {
            "result": "success"
        }
