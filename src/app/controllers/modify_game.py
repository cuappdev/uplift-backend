from . import *
from datetime import datetime as dt


class ModifyGameController(AppDevController):
    def get_path(self):
        return "/modify_game/"

    def get_methods(self):
        return ["POST"]

    def content(self, **kwargs):
        game_id = request.form["game_id"]
        title = request.form["title"]
        text = request.form["text"]
        time = dt.strptime(request.form["time"], "%Y-%m-%d, %H:%M")
        location = request.form["location"]
        max_players = request.form["max_players"]

        game = game_dao.get_game_by_id(game_id)
        if title:
            game.title = title
        if text:
            game.text = text
        if time:
            game.time = time
        if location:
            game.location = location
        if max_players:
            game.max_players = max_players

        db_utils.commit_model(game)
        db.session.commit()
        return {"result": "success"}
