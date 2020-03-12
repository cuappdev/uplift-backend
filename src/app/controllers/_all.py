from src.app.controllers.create_game import *
from src.app.controllers.create_reply import *
from src.app.controllers.create_user import *
from src.app.controllers.delete_game import *
from src.app.controllers.delete_reply import *
from src.app.controllers.get_all_games import *
from src.app.controllers.get_all_posts import *
from src.app.controllers.get_all_routines import *
from src.app.controllers.get_all_social_media import *
from src.app.controllers.get_games_by_user import *
from src.app.controllers.get_post_by_id import *
from src.app.controllers.get_replies_by_game import *
from src.app.controllers.get_routine_by_id import *
from src.app.controllers.get_routine_by_post_id import *
from src.app.controllers.get_social_media_by_id import *
from src.app.controllers.get_social_media_by_post_id import *
from src.app.controllers.get_user_by_id import *
from src.app.controllers.initialize_session_controller import *
from src.app.controllers.join_game import *
from src.app.controllers.modify_game import *
from src.app.controllers.modify_reply import *
from src.app.controllers.update_session_controller import *

controllers = [
    CreateGameController(),
    CreateReplyController(),
    CreateUserController(),
    DeleteGameController(),
    DeleteReplyController(),
    GetAllGamesController(),
    GetAllPostsController(),
    GetAllRoutinesController(),
    GetAllSocialMediaController(),
    GetGamesByUserController(),
    GetPostByIdController(),
    GetRepliesByGame(),
    GetRoutineByIdController(),
    GetRoutineByPostIdController(),
    GetSocialMediaByIdController(),
    GetSocialMediaByPostIdController(),
    GetUserByIDController(),
    InitializeSessionController(),
    JoinGameController(),
    ModifyGameController(),
    ModifyReplyController(),
    UpdateSessionController(),
]
