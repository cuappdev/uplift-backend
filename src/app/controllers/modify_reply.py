from . import *


class ModifyReplyController(AppDevController):
    def get_path(self):
        return "/modify_reply/"

    def get_methods(self):
        return ["POST"]

    def content(self, **kwargs):
        reply_id = request.form["reply_id"]
        reply = reply_dao.get_reply_by_id(reply_id)
        if not reply:
            return {
                "result": "fail",
                "error": "reply not found"
            }

        text = request.form["text"]

        if text:
            reply.text = text

        db.session.commit()
        return {"result": "succes"}
