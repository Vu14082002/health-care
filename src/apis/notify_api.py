from src.core import HTTPEndpoint
from src.core.security.authentication import JsonWebToken
from src.factory import Factory


class NotificationApi(HTTPEndpoint):
    async def get(self,  auth:JsonWebToken):
        _user_id= auth.get("id")
        _notification_helper = await Factory().get_notification_helper()
        _result =await _notification_helper.get_all_notifications(_user_id)
        return {"items":_result,"total":len(_result),"unread":0}

class NotificationUnreadApi(HTTPEndpoint):
    async def get(self, auth: JsonWebToken):
        _user_id = auth.get("id")
        _notification_helper = await Factory().get_notification_helper()
        _total= await _notification_helper.get_all_unread_notifications(_user_id)
        return {"unread": _total}
