
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func, insert

from src.core import logger
from src.enum import MessageTemplate
from src.models.notification_model import NotificationModel


class NotificationRepository:


    @staticmethod
    async def insert_notification(
        session: AsyncSession,
        user_receive: int,
        message: str,
        title: str | None = None,
    ):
        try:
            if not title:
                title = MessageTemplate.NOTiFY_TITLE.value
            _insert_query = insert(NotificationModel).values(user_id=user_receive, title=title, message=message).returning(NotificationModel)
            result = await session.execute(_insert_query)
            data = result.scalar_one()
            return data
        except Exception as e:
            logger.info(f"Error: when insert notification {e}")
            print(e)
            return None

    @staticmethod
    async def get_total_message_unread(session: AsyncSession, user_id: int):
        try:
            _select_query = select(func.count(NotificationModel.id)).where(NotificationModel.user_id == user_id, NotificationModel.is_read == False)
            _result_query = await session.execute(_select_query)
            data = _result_query.scalar_one()
            return data
        except Exception as e:
            logger.info(f"Error: when get total message unread {e}")
            print(e)
            return 0
