from . import *


class GetSocialMediaByIdController(AppDevController):
    def get_path(self):
        return "/social_media/<social_media_id>/"

    def get_methods(self):
        return ["GET"]

    def content(self, **kwargs):
        social_media_id = request.view_args["social_media_id"]
        social_media = social_media_dao.get_social_media_by_id(social_media_id)
        return social_media_dao.serialize_social_media(social_media)
