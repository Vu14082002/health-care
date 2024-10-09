from collections import defaultdict

from sqlalchemy import and_, exists, or_, select
from sqlalchemy.orm import joinedload

from src.core.database.postgresql import PostgresRepository
from src.core.decorator.exception_decorator import (
    catch_error_repository,
    exception_handler,
)
from src.core.exception import BadRequest
from src.enum import ErrorCode
from src.models.appointment_model import AppointmentModel
from src.models.conversation_model import ConversationModel
from src.schema.conversation_schema import RequestGetAllConversationSchema


class ConversationRepoitory(PostgresRepository[ConversationModel]):

    @catch_error_repository
    async def create_conversation(self, user_create: int, appointment_id: int):
        # check appointment_id exist
        query_appointment = select(
            exists().where(
                and_(
                    AppointmentModel.id == appointment_id,
                    or_(
                        AppointmentModel.doctor_id == user_create,
                        AppointmentModel.patient_id == user_create,
                    ),
                )
            )
        )
        result = await self.session.execute(query_appointment)
        is_exist = result.scalar_one_or_none()
        if not is_exist:
            raise BadRequest(
                error_code=ErrorCode.NOT_FOUND.name,
                errors={
                    "message": "Appointment not found or you are not permission to create conversation this appointment"
                },
            )

        query_find_conversation = (
            select(ConversationModel)
            .where(ConversationModel.appointment_id == appointment_id)
            .options(
                joinedload(ConversationModel.appointment),
                joinedload(ConversationModel.messages),
            )
        )
        result_query_find_conversation = await self.session.execute(
            query_find_conversation
        )

        conversation_model = (
            result_query_find_conversation.unique().scalar_one_or_none()
        )
        if conversation_model:
            data = self._get_conversation_details(conversation_model, user_create)
            return data
        # create new conversation id not exist\
        appointment = await self.session.get(AppointmentModel, appointment_id)
        new_conversation = ConversationModel()
        new_conversation.appointment = appointment
        self.session.add(new_conversation)
        await self.session.commit()
        return self._get_conversation_details(
            conversation_model, user_create, appointment
        )

    def _get_conversation_details(
        self,
        conversation_model: ConversationModel,
        user_create: int,
        appointment: AppointmentModel | None = None,
    ):
        appointment = conversation_model.appointment if not appointment else appointment
        participant = (
            appointment.doctor
            if appointment.doctor_id != user_create
            else appointment.patient
        )
        participant = (
            appointment.doctor
            if appointment.doctor_id != user_create
            else appointment.patient
        )

        latest_message = None
        unread = 0
        for message in conversation_model.messages:
            if message.sender_id != user_create and not message.is_read:
                unread += 1
            if not latest_message or message.created_at > message.created_at:
                latest_message = message
        data = {
            **conversation_model.as_dict,
            "users": [
                appointment.doctor_id,
                appointment.patient_id,
            ],
            "participant": {**participant.as_dict},
            "latest_message": {**latest_message.as_dict} if latest_message else {},
            "unread": unread,
        }
        return data

    @exception_handler
    async def get_conversation(
        self, user_id: int, query_params: RequestGetAllConversationSchema
    ):
        query_conversation = (
            select(ConversationModel)
            .join(ConversationUserModel)
            .where(ConversationUserModel.user_id == user_id)
            .options(joinedload(ConversationModel.messages))
        )
        result_query = await self.session.execute(query_conversation)

        data_result_qurey = result_query.unique().scalars().all()

        items = []
        for item in data_result_qurey:
            data_dict = defaultdict()
            latest_message = item.latest_message
            data_dict.update(
                {
                    "conversation_id": item.id,
                    "latest_message": (
                        latest_message.as_dict if latest_message else None
                    ),
                }
            )
            items.append(data_dict)
        return items

    async def get_users_from_conversation(self, conversation_id: int):
        query_conversation = select(ConversationUserModel.user_id).where(
            ConversationUserModel.conversation_id == conversation_id
        )
        result_query = await self.session.execute(query_conversation)
        data_result_query = result_query.scalars().all()
        return data_result_query
