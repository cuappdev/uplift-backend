from src.app.controllers.get_all_posts import *
from src.app.controllers.get_all_routines import *
from src.app.controllers.get_all_social_media import *
from src.app.controllers.get_post_by_id import *
from src.app.controllers.get_routine_by_id import *
from src.app.controllers.get_routine_by_post_id import *
from src.app.controllers.get_social_media_by_id import *
from src.app.controllers.get_social_media_by_post_id import *
from src.app.controllers.initialize_session_controller import *
from src.app.controllers.update_session_controller import *

controllers = [
  GetAllPostsController(),
  GetAllRoutinesController(),
  GetAllSocialMediaController(),
  GetPostByIdController(),
  GetRoutineByIdController(),
  GetRoutineByPostIdController(),
  GetSocialMediaByIdController(),
  GetSocialMediaByPostIdController(),
  InitializeSessionController(),
  UpdateSessionController()
]
