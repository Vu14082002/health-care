import datetime

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
from src.models.doctor_model import DoctorModel
from src.models.patient_model import PatientModel
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
            data = await self._get_conversation_details(conversation_model, user_create)
            return data
            # create new conversation id not exist\
        query_appointment = (
            select(AppointmentModel)
            .where(AppointmentModel.id == appointment_id)
            .options(joinedload(AppointmentModel.work_schedule))
        )
        result_query_appointment = await self.session.execute(query_appointment)
        data_query_appointment = result_query_appointment.unique().scalar_one()

        name_conversation = f"{data_query_appointment.name} - {data_query_appointment.work_schedule.examination_type} - {data_query_appointment.work_schedule.work_date}"
        appointment = await self.session.get(AppointmentModel, appointment_id)
        new_conversation = ConversationModel()
        new_conversation.appointment = appointment
        new_conversation.name = name_conversation
        self.session.add(new_conversation)
        await self.session.commit()
        return await self._get_conversation_details(
            new_conversation, user_create, appointment, True
        )

    async def _get_conversation_details(
        self,
        conversation_model: ConversationModel,
        user_create: int,
        appointment: AppointmentModel | None = None,
        is_new: bool = False,
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
        if not is_new:
            for message in conversation_model.messages:
                if message.sender_id != user_create and not message.is_read:
                    unread += 1
                if not latest_message or message.created_at > message.created_at:
                    latest_message = message
        if latest_message:
            user_sender_query = await self.session.execute(
                select(PatientModel).where(PatientModel.id == latest_message.sender_id)
            )
            result_user_sender_query = user_sender_query.unique().scalar_one_or_none()
            if not result_user_sender_query:
                user_sender_query = await self.session.execute(
                    select(DoctorModel).where(
                        DoctorModel.id == latest_message.sender_id
                    )
                )
                result_user_sender_query = (
                    user_sender_query.unique().scalar_one_or_none()
                )
                exclue_fields = [
                    "certification",
                    "verify_status",
                    "is_local_person",
                    "diploma",
                    "type_of_disease",
                    "hopital_address_work",
                    "address",
                    "description",
                    "license_number",
                    "education",
                    "account_number",
                    "bank_name",
                    "beneficiary_name",
                    "branch_name",
                    "created_at",
                    "updated_at",
                    "is_deleted",
                ]
                create_at = datetime.datetime.fromtimestamp(
                    latest_message.created_at, datetime.timezone.utc
                )
                latest_message = {
                    **latest_message.as_dict,
                    "sender": {
                        k: v
                        for k, v in result_user_sender_query.as_dict.items()
                        if k not in exclue_fields
                    },
                    "created_at": create_at.isoformat(),
                }
        data = {
            **conversation_model.as_dict,
            "users": [
                appointment.doctor_id,
                appointment.patient_id,
            ],
            "participant": {**participant.as_dict},
            "latest_message": latest_message if latest_message else {},
            "unread": unread,
        }
        return data

    @exception_handler
    async def get_conversation(
        self, user_id: int, query_params: RequestGetAllConversationSchema
    ):
        query_appointment = (
            select(AppointmentModel)
            .where(
                or_(
                    AppointmentModel.doctor_id == user_id,
                    AppointmentModel.patient_id == user_id,
                )
            )
            .options(
                joinedload(AppointmentModel.conversation).joinedload(
                    ConversationModel.messages
                )
            )
            .order_by(AppointmentModel.created_at.desc())
        )
        result_query_appointment = await self.session.execute(query_appointment)
        data_result_query_appointment = (
            result_query_appointment.unique().scalars().all()
        )
        items = []
        for appointment in data_result_query_appointment:
            if appointment.conversation is None:
                continue
            # name_conversation = f"{appointment.name} - {appointment.work_schedule.examination_type} - {appointment.work_schedule.work_date}"
            data = await self._get_conversation_details(
                appointment.conversation, user_id, appointment
            )
            items.append(
                {
                    **data,
                }
            )
        return items

    async def get_users_from_conversation(self, conversation_id: int):
        return [1, 2, 3, 4]
