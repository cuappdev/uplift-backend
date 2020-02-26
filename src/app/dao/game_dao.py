from . import *


def get_all_games():
    return Game.query.all()

def get_game_by_id(game_id):
    return Game.query.filter(Game.id == game_id).first()

def serialize_game(game):
    return game_schema.dump(game)


def create_game(**kwargs):
    new_game = Game(
        user_id=kwargs.get("user_id"),
        text=kwargs.get("text", ""),
        title=kwargs.get("title", ""),
        time=kwargs.get("time"),
        location=kwargs.get("location"),
        max_players=kwargs.get("max_players"),
    )
    db_utils.commit_model(new_game)
    return True, new_game
