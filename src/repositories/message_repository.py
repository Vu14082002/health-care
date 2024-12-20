import logging
from collections import defaultdict
from typing import Any

from sqlalchemy import exists, select
from sqlalchemy.orm import joinedload

from src.core.database.postgresql import PostgresRepository
from src.core.decorator.exception_decorator import (
    catch_error_repository,
)
from src.core.exception import BadRequest, InternalServer
from src.enum import ErrorCode, MessageContentSchema
from src.helper.socket_api_helper import SocketServiceHelper
from src.models.conversation_model import ConversationModel
from src.models.message_model import MessageModel
from src.models.user_model import UserModel
from src.repositories.notification_repository import NotificationRepository

img_admin = "https://png.pngtree.com/png-clipart/20230409/original/pngtree-admin-and-customer-service-job-vacancies-png-image_9041264.png"


class MessageRepository(PostgresRepository[MessageModel]):
    async def get_messages_from_conversation(self, conversation_id: int):
        try:
            query_message = (
                select(MessageModel)
                .options(
                    joinedload(MessageModel.sender),
                )
                .where(MessageModel.conversation_id == conversation_id)
            )
            result_query_message = await self.session.execute(query_message)
            data_result_query_message = result_query_message.scalars().all()
            items: list[dict[str, Any]] = []
            items_users = defaultdict()
            for message in data_result_query_message:
                sender_id_str = str(message.sender_id)
                if items_users.get(sender_id_str, None) is None:
                    query_get_user = (
                        select(UserModel)
                        .where(UserModel.id == message.sender_id)
                        .options(
                            joinedload(UserModel.doctor),
                            joinedload(UserModel.patient),
                        )
                    )
                    result_query_message = await self.session.execute(query_get_user)
                    data_result_query_message = result_query_message.scalar_one()
                    sender_dict = {}
                    if data_result_query_message.doctor:
                        sender_dict = {
                            "first_name": data_result_query_message.doctor.first_name,
                            "last_name": data_result_query_message.doctor.last_name,
                            "avatar": data_result_query_message.doctor.avatar,
                            "phone_number": data_result_query_message.doctor.phone_number,
                        }
                    elif data_result_query_message.patient:
                        sender_dict = {
                            "first_name": data_result_query_message.patient.first_name,
                            "last_name": data_result_query_message.patient.last_name,
                            "avatar": data_result_query_message.patient.avatar,
                            "phone_number": data_result_query_message.phone_number,
                        }
                    # for role admin
                    # else:
                    #     sender_dict = {
                    #         "first_name": "Quan Tri",
                    #         "last_name": "Vien",
                    #         "avatar": img_admin,
                    #         "phone_number": data_result_query_message.phone_number,
                    #     }
                    items_users[sender_id_str] = sender_dict
                item = {
                    "sender": items_users.get(sender_id_str),
                    **message.as_dict,
                }
                items.append(item)
            return items
        except (BadRequest, InternalServer) as e:
            logging.error(e)
            raise e
        except Exception as e:
            logging.error(e)
            raise InternalServer(
                error_code=ErrorCode.UNKNOWN_ERROR.name,
                errors={"message": "Internal server error"},
            )

    @catch_error_repository("Failed to create message, please try again later")
    async def create_message(
        self,
        sender_id: int,
        conversation_id: str,
        reply_id: int | None,
        message: MessageContentSchema,
        first_name: str | None,
        last_name: str | None,
        avatar: str | None,
        phone_number: str | None,
    ):
        if reply_id:
            check_message_exist = select(exists().where(MessageModel.id == reply_id))
            result_check_message_exist = await self.session.execute(check_message_exist)
            data_result_check_message_exist = result_check_message_exist.scalar_one()
            if not data_result_check_message_exist:
                raise BadRequest(
                    error_code=ErrorCode.NOT_FOUND.name,
                    errors={"message": "Reply message not found"},
                )
        # check conversation exist
        conversation = (
            select(ConversationModel)
            .where(ConversationModel.id == conversation_id)
            .options(joinedload(ConversationModel.appointment))
        )
        result_conversation = await self.session.execute(conversation)
        data_result_conversation = result_conversation.scalar_one_or_none()
        if not data_result_conversation:
            raise BadRequest(
                error_code=ErrorCode.NOT_FOUND.name,
                errors={"conversation": "Conversation not found"},
            )
        message_data = MessageModel(
            sender_id=sender_id,
            conversation_id=conversation_id,
            reply_id=reply_id,
            is_read=False,
            message=message.model_dump(),
        )
        _ = self.session.add(message_data)

        # get user id from notification
        _appointment = data_result_conversation.appointment
        _user_receive_id = _appointment.doctor_id if sender_id == _appointment.patient_id else _appointment.patient_id
        # save message into notification
        _user_model = await self.session.execute(
            select(UserModel).where(UserModel.id == sender_id).options(
                joinedload(UserModel.doctor), joinedload(UserModel.patient)
            )
        )
        _user_model = _user_model.scalar_one()
        _message=""
        if _user_model.doctor:
            _message = (
                "Bác sĩ "
                + _user_model.doctor.first_name
                + " "
                + _user_model.doctor.last_name
                + " đã gửi tin nhắn cho bạn"
            ) # type: ignore
        elif _user_model.patient:
            _message = (
                "Bệnh nhân "
                + _user_model.patient.last_name
                + " "
                + _user_model.patient.first_name
                + " đã gửi tin nhắn cho bạn"
            ) # type: ignore
        # send notify
        _notify_model = await NotificationRepository.insert_notification(
            session=self.session, user_receive=_user_receive_id, message=_message
        )
        await self.session.commit()
        if _notify_model:
            total_message_unread = await NotificationRepository.get_total_message_unread(
                self.session, _user_receive_id
            )
            socket_service_helper = SocketServiceHelper()
            socket_service_helper.send_notify_helper(
                _notify_model, total_message_unread
            )
        appointment = data_result_conversation.appointment
        return {
            **message_data.as_dict,
            "users": [appointment.doctor_id, appointment.patient_id],
            "sender": {
                "first_name": first_name,
                "last_name": last_name,
                "avatar": avatar,
                "phone_number": phone_number,
            },
        }
