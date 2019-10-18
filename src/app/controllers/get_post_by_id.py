from . import *


class GetPostByIdController(AppDevController):
    def get_path(self):
        return "/post/<post_id>/"

    def get_methods(self):
        return ["GET"]

    def content(self, **kwargs):
        post = post_dao.get_post_by_id(request.view_args["post_id"])
        return post_dao.serialize_post(post)
