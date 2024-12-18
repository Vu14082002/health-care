
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func, insert

from src.core import logger
from src.core.database.postgresql import PostgresRepository
from src.core.decorator.exception_decorator import catch_error_repository
from src.enum import MessageTemplate
from src.models.notification_model import NotificationModel


class NotificationRepository(PostgresRepository[NotificationModel]):


    @catch_error_repository(None)
    async def get_all_notifications(self, user_id: int):
        # mark as read
        #
        update_notification_query = (
            update(NotificationModel)
            .where(NotificationModel.user_id == user_id)
            .values(is_read=True)
            .returning(NotificationModel)
        )
        executed_update_result = await self.session.execute(update_notification_query)
        updated_notifications = executed_update_result.scalars().all()
        await self.session.commit()
        _sort_data = sorted(
            [self._format_data(item) for item in updated_notifications],
            key=lambda x: x["created_at"],
            reverse=True,
        )
        return _sort_data

    def _format_data(self, data:NotificationModel):
        # utc because we database store in utc +7 so we need to convert to utc
        _create_date_fmt = datetime.fromtimestamp(
            data.created_at, tz=timezone.utc
        ).isoformat()
        return {
            "id": data.id,
            "title": data.title,
            "message": data.message,
            "is_read": data.is_read,
            "created_at": _create_date_fmt,
        }

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
