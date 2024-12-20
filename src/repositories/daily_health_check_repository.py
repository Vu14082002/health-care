import logging
from datetime import date

from sqlalchemy import exists, func, insert, select, update
from sqlalchemy.orm import joinedload

from src.core.database.postgresql import PostgresRepository
from src.core.decorator.exception_decorator import catch_error_repository
from src.core.exception import BadRequest, InternalServer
from src.enum import ErrorCode, MessageTemplate
from src.helper.socket_api_helper import SocketServiceHelper
from src.models.appointment_model import AppointmentModel
from src.models.daily_health_check_model import DailyHealCheckModel
from src.models.patient_model import PatientModel
from src.repositories.notification_repository import NotificationRepository
from src.schema.daily_health_check_schema import (
    DailyHealthCheckSchema,
    RequestGetAllDailyHealthSchema,
)


class DailyHealthCheckRepository(PostgresRepository[DailyHealCheckModel]):


    @catch_error_repository(message=None)
    async def create_one(self, data_schema: DailyHealthCheckSchema):
        # check patient exist
        # check_exist = select(
        #     exists().where(
        #         AppointmentModel.patient_id == data_schema.patient_id,
        #         AppointmentModel.id == data_schema.appointment_id,
        #     )
        # )
        # result_check_exist = await self.session.execute(check_exist)
        # is_patient_exist = result_check_exist.scalar()
        # if not is_patient_exist:
        #     raise BadRequest(
        #         error_code=ErrorCode.NOT_FOUND.name,
        #         errors={
        #             "message": "appointment not have with this patient, or patient is not owner by this appointment"
        #         },
        #     )
        _appointment_query = (
            select(AppointmentModel)
            .where(
                AppointmentModel.patient_id == data_schema.patient_id,
                AppointmentModel.id == data_schema.appointment_id,
            )
            .options(
                joinedload(AppointmentModel.doctor),
                joinedload(AppointmentModel.patient),
            )
        )
        _appointment_result = await self.session.execute(_appointment_query)
        _appointment = _appointment_result.scalar_one_or_none()
        if not _appointment:
            raise BadRequest(
                error_code=ErrorCode.NOT_FOUND.name,
                errors={
                    "message": "appointment not have with this patient, or patient is not owner by this appointment"
                },
            )
        # check user have create in date if created will update
        date_check = date.today()
        if data_schema.date_create:
            date_check = data_schema.date_create

        query_daily_check = select(DailyHealCheckModel).where(
            DailyHealCheckModel.patient_id == data_schema.patient_id,
            DailyHealCheckModel.date_create == date_check,
        )
        result_daily_check = await self.session.execute(query_daily_check)
        data_result_daily_check = result_daily_check.scalars().all()
        data_len = len(data_result_daily_check)

        _notification_model=None
        _socket_service_helper = SocketServiceHelper()
        if data_len > 1:
            raise BadRequest(
                error_code=ErrorCode.INVALID_REQUEST.name,
                errors={
                    "message": ErrorCode.msg_duplicate_daily_health_check.value,
                },
            )
        elif data_len == 1:
            # logic update
            update_data = (
                update(DailyHealCheckModel)
                .where(DailyHealCheckModel.id == data_result_daily_check[0].id)
                .values(**data_schema.model_dump(exclude={"id"}))
            )
            _ = await self.session.execute(update_data)
            # create notification
            _message: str = f"Bệnh nhân {_appointment.patient.last_name} {_appointment.patient.first_name} vừa cập nhật hồ sơ sức khỏe hàng ngày"
            _notification_model = await NotificationRepository.insert_notification(
                session=self.session,
                user_receive=_appointment.doctor_id,
                title="Thông báo",
                message=_message,
            )
            await self.session.commit()
            _total_unread = await NotificationRepository.get_total_message_unread(
                session=self.session, user_id=_appointment.doctor_id
            )
            _socket_service_helper.send_notify_helper(
                _notification_model, _total_unread
            )
            return {
                "message": "Hồ sơ sức khỏe hàng ngày đã được cập nhật thành công",
            }
        else:
            # logic insert
            insert_data = insert(DailyHealCheckModel).values(
                **data_schema.model_dump()
            )
            result_insert_data = await self.session.execute(insert_data)
            # create notification
            _message: str = f"Bệnh nhân {_appointment.patient.last_name} {_appointment.patient.first_name} vừa tạo hồ sơ sức khỏe hàng ngày"
            _notification_model = await NotificationRepository.insert_notification(
                session=self.session,
                user_receive=_appointment.doctor_id,
                title=MessageTemplate.NOTiFY_TITLE.value,
                message=_message,
            )
            await self.session.commit()
            _total_unread = await NotificationRepository.get_total_message_unread(
                session=self.session, user_id=_appointment.doctor_id
            )
            _socket_service_helper.send_notify_helper(
                _notification_model, _total_unread
            )
            _ = result_insert_data.scalars().first()

            return {
                "message": "Hồ sơ sức khỏe hàng ngày đã được tạo thành công",
            }

    async def get_all_daily_health_check_by_role(
        self, query_params: RequestGetAllDailyHealthSchema, doctor_id: int | None
    ):
        try:
            # check patient exist
            patient_query = select(PatientModel).where(
                PatientModel.id == query_params.patient_id
            )

            result_patient_query = await self.session.execute(patient_query)
            data_result_patient_query = result_patient_query.scalar_one_or_none()
            if not data_result_patient_query:
                raise BadRequest(
                    error_code=ErrorCode.NOT_FOUND.name,
                    errors={"message": "Patient not found"},
                )

            if doctor_id and data_result_patient_query.doctor_manage_id != doctor_id:
                raise BadRequest(
                    error_code=ErrorCode.UNAUTHORIZED.name,
                    errors={"message": "You are not permitted to acticate this patient"},
                )
            # bs logic
            daily_query = select(DailyHealCheckModel).where(
                DailyHealCheckModel.patient_id == query_params.patient_id,
                DailyHealCheckModel.appointment_id == query_params.appointment_id,
            )

            if query_params.create_date:
                daily_query = daily_query.where(
                    DailyHealCheckModel.date_create == query_params.create_date
                )
            if query_params.start_date:
                daily_query = daily_query.where(
                    DailyHealCheckModel.date_create >= query_params.start_date
                )
            if query_params.end_date:
                daily_query = daily_query.where(
                    DailyHealCheckModel.date_create <= query_params.end_date
                )
            total_count_query = select(func.count()).select_from(daily_query)

            # pagination
            daily_query = daily_query.offset(
                (query_params.current_page - 1) * query_params.page_size
            ).limit(query_params.page_size)
            result_daily_query = await self.session.execute(daily_query)
            data_result_patient_query = result_daily_query.scalars().all()
            # count total pages
            result_total_count_query = await self.session.execute(total_count_query)
            total_pages = (
                result_total_count_query.scalar_one() + query_params.page_size - 1
            ) // query_params.page_size
            return {
                "items": [item.as_dict for item in data_result_patient_query],
                "current_page": query_params.current_page,
                "page_size": query_params.page_size,
                "total_pages": total_pages,
            }
        except (BadRequest, InternalServer) as e:
            logging.error(e)
            raise e
        except Exception as e:
            logging.error(e)
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={
                    "message": "Server currently unable to handle this request,please try again later"
                },
            )
