from . import *
from datetime import datetime as dt


class CreateGameController(AppDevController):
    def get_path(self):
        return "/create_game/"

    def get_methods(self):
        return ["POST"]

    def content(self, **kwargs):
        user_id = request.form.get("user_id")
        title = request.form.get("title")
        text = request.form.get("text")
        time = dt.strptime(request.form.get("time"), "%Y-%m-%d, %H:%M")
        location = request.form.get("location")
        max_players = request.form.get("max_players")

        _, game = game_dao.create_game(
            user_id=user_id, text=text, time=time, title=title, location=location, max_players=max_players
        )

        user = users_dao.get_user_by_id(user_id)
        game.players.append(user)
        user.games.append(game)

        db.session.commit()
        return utils.success_response(game_dao.serialize_game(game))
