from . import *


class DeleteReplyController(AppDevController):
    def get_path(self):
        return "/delete_reply/"

    def get_methods(self):
        return ["POST"]

    def content(self, **kwargs):
        reply_id = request.form.get("reply_id")
        reply = reply_dao.get_reply_by_id(reply_id)

        db.session.delete(reply)
        db.session.commit()

        return utils.success_response("deleted")
