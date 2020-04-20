from . import *


class JoinGameController(AppDevController):
    def get_path(self):
        return "/join_game/"

    def get_methods(self):
        return ["POST"]

    def content(self, **kwargs):
        user_id = request.form.get("user_id")
        game_id = request.form.get("game_id")

        game = game_dao.get_game_by_id(game_id)
        user = users_dao.get_user_by_id(user_id)

        # Game is full
        if len(game.players) >= game.max_players:
            return utils.failure_response("Game is full")

        # User already joined
        if user in game.players:
            return utils.failure_response("User already joined")

        game.players.append(user)
        user.games.append(game)

        db.session.commit()
        return utils.success_response(game_dao.serialize_game(game))
