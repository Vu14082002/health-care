
from datetime import datetime

import pytz
from sqlalchemy import desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func, insert

from src.core import logger
from src.core.database.postgresql import PostgresRepository
from src.core.decorator.exception_decorator import catch_error_repository
from src.core.exception import BadRequest
from src.enum import ErrorCode, MessageTemplate
from src.models.notification_model import NotificationModel


class NotificationRepository(PostgresRepository[NotificationModel]):


    @catch_error_repository(None)
    async def get_all_notifications(self, user_id: int):
        _select_query = (
            select(NotificationModel)
            .where(NotificationModel.user_id == user_id)
            .order_by(desc(NotificationModel.created_at))
        )
        executed_query_result = await self.session.execute(_select_query)
        _notifications = executed_query_result.scalars().all()
        # await self.session.commit()
        # {"items": _result, "total": len(_result), "unread": 0}
        items=[]
        unread= 0
        for item in _notifications:
            if not item.is_read:
                unread+=1
            items.append(self._format_data(item))
        return {"items": items, "total": len(items), "unread": unread}

    def _format_data(self, data:NotificationModel):
        # FIXME for ec2 instance
        _create_date_fmt = datetime.fromtimestamp(
            data.created_at, tz=pytz.timezone("Asia/Ho_Chi_Minh")
        ).isoformat()
        return {
            "id": data.id,
            "title": data.title,
            "message": data.message,
            "is_read": data.is_read,
            "created_at": _create_date_fmt,
        }

    @catch_error_repository(None)
    async def update_read_notification(self, notification_id: int, user_id: int):
        _update_query = (
            update(NotificationModel)
            .where(NotificationModel.id == notification_id, NotificationModel.user_id == user_id)
            .values(is_read=True)
            .returning(NotificationModel)
        )
        executed_query_result = await self.session.execute(_update_query)
        _notification = executed_query_result.scalars().first()
        await self.session.commit()
        if _notification:
            return self._format_data(_notification)
        raise BadRequest(
            error_code=ErrorCode.NOT_FOUND.name,
            errors={"message": ErrorCode.msg_notification_not_found.value},
        )

    @catch_error_repository(None)
    async def update_all_read_notification(self, user_id: int):
        _update_query = (
            update(NotificationModel)
            .where(NotificationModel.user_id == user_id)
            .values(is_read=True).returning(NotificationModel)
        )
        execute_update_notification = await self.session.execute(_update_query)
        _notifications = execute_update_notification.scalars().all()
        await self.session.commit()
        items = []
        for item in _notifications:
            items.append(self._format_data(item))
        items = sorted(items, key=lambda x: x["id"], reverse=True)
        return {"items": items, "total": len(items), "unread": 0}
    @staticmethod
    async def insert_notification(
        session: AsyncSession,
        user_receive: int,
        message: str,
        title: str | None = None,
    ):
        try:
            _current_datetime = int(
                datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).timestamp()
            )
            if not title:
                title = MessageTemplate.NOTiFY_TITLE.value
            _insert_query = insert(NotificationModel).values(user_id=user_receive, title=title, message=message,created_at=_current_datetime,updated_at=_current_datetime).returning(NotificationModel)
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
