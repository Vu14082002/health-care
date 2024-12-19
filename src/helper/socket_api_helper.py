

from datetime import datetime, timezone

import requests

from src.config import config
from src.core import logger
from src.models.notification_model import NotificationModel


class SocketServiceHelper:
    def __init__(self) -> None:
        self.base_url = config.BASE_URL_CHAT_SERVICE

    def send_notify_helper(self,notifyModel:NotificationModel,total_unread:int):
        try:
            url_socket = f"{self.base_url}/api/notify"
            _create_date = datetime.fromtimestamp(notifyModel.created_at, tz=timezone.utc)
            _data_json={
                    "userId":notifyModel.user_id,
                    "id":notifyModel.id,
                    "title":notifyModel.title,
                    "message":notifyModel.message,
                    "totalUnread":total_unread,
                    "createdAt":_create_date.isoformat()
                }
            _data_response = requests.post(url_socket, json=_data_json)
            if _data_response.status_code == 200:
                logger.info("Send notify success")
            else:
                logger.info("Send notify fail")
        except Exception as e:
            logger.error(f"Error: {e}")
