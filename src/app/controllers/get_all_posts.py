from . import *


class GetAllPostsController(AppDevController):
    def get_path(self):
        return "/posts/"

    def get_methods(self):
        return ["GET"]

    def content(self, **kwargs):
        posts = post_dao.get_all_posts()
        return [post_dao.serialize_post(p) for p in posts]
