from src.core import HTTPEndpoint
from src.core.security.authentication import JsonWebToken
from src.factory import Factory
from src.schema.notification_schema import NotificationSchemaUPdateToRead


class NotificationApi(HTTPEndpoint):
    async def get(self,  auth:JsonWebToken):
        _user_id= auth.get("id")
        _notification_helper = await Factory().get_notification_helper()
        _result =await _notification_helper.get_all_notifications(_user_id)
        return _result
class NotificationReadApi(HTTPEndpoint):
    async def put(self, form_data: NotificationSchemaUPdateToRead, auth: JsonWebToken):
        _user_id = auth.get("id")
        _notification_helper = await Factory().get_notification_helper()
        _result = await _notification_helper.update_read_notification(notification_id=form_data.notification_id, user_id=_user_id)
        return _result
class NotificationUnreadApi(HTTPEndpoint):
    async def get(self, auth: JsonWebToken):
        _user_id = auth.get("id")
        _notification_helper = await Factory().get_notification_helper()
        _total= await _notification_helper.get_all_unread_notifications(_user_id)
        return {"unread": _total}
