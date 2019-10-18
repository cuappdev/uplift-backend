from . import *


class GetAllSocialMediaController(AppDevController):
    def get_path(self):
        return "/social_media/"

    def get_methods(self):
        return ["GET"]

    def content(self, **kwargs):
        social_media = social_media_dao.get_all_social_media()
        return [social_media_dao.serialize_social_media(s) for s in social_media]
