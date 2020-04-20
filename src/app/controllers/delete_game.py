from . import *


class DeleteGameController(AppDevController):
    def get_path(self):
        return "/delete_game/"

    def get_methods(self):
        return ["POST"]

    def content(self, **kwargs):
        game_id = request.form.get("game_id")
        game = game_dao.get_game_by_id(game_id)

        db.session.delete(game)
        db.session.commit()

        return utils.success_response("deleted")
