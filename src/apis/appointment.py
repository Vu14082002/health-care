import logging as log

from src.core import HTTPEndpoint
from src.core.exception import BadRequest, BaseException, Forbidden, InternalServer
from src.core.security.authentication import JsonWebToken
from src.enum import ErrorCode, Role
from src.factory import Factory
from src.helper.appointment_helper import AppointmentHelper
from src.schema.appointment_schema import (
    RequestGetAllAppointmentSchema,
    RequestRegisterAppointment,
)


class AppointmentApiGET(HTTPEndpoint):
    async def get(
        self, query_params: RequestGetAllAppointmentSchema, auth: JsonWebToken
    ):
        '''
        this api is used to get all appointments, only admin, doctor and patient can get all appointments
        '''
        try:
            appointment_helper: AppointmentHelper = (
                await Factory().get_appointment_helper()
            )
            user_role = auth.get("role", "")
            user_id = auth.get("id")

            if user_role not in [
                Role.ADMIN.value,
                Role.DOCTOR.value,
                Role.PATIENT.value,
            ]:
                raise Forbidden(
                    error_code=ErrorCode.UNAUTHORIZED.name,
                    errors={"message": ErrorCode.msg_permission_denied.value},
                )

            filter_params = query_params.model_dump()
            appointments = {}
            if user_role == Role.ADMIN.value:
                appointments = await appointment_helper.get_all_appointments(
                    **filter_params
                )
            elif user_role == Role.DOCTOR.value:
                filter_params["doctor_id"] = user_id
                appointments = await appointment_helper.get_all_appointments(
                    **filter_params
                )
            elif user_role == Role.PATIENT.value:
                filter_params["patient_id"] = user_id
                appointments = await appointment_helper.get_all_appointments(
                    **filter_params
                )
            return appointments
        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            log.error(e)
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            ) from e


class AppointmentApi(HTTPEndpoint):
    async def post(self, form_data: RequestRegisterAppointment, auth: JsonWebToken):
        '''
        this api is used to create appointment, only admin and patient can create appointment
        '''
        try:
            user_role = auth.get("role", "")
            if user_role not in [Role.ADMIN.value, Role.PATIENT.value]:
                raise Forbidden(
                    error_code=ErrorCode.UNAUTHORIZED.name,
                    errors={"message": ErrorCode.msg_server_error.value},
                )

            if user_role == Role.ADMIN.value and not form_data.patient_id:
                raise Forbidden(
                    error_code=ErrorCode.UNAUTHORIZED.name,
                    errors={"message": "patient_id is required for admin"},
                )
            patient_id: int | None = (
                form_data.patient_id if user_role == "ADMIN" else auth.get("id")
            )
            if patient_id is None:
                raise BadRequest(
                    error_code=ErrorCode.BAD_REQUEST.name,
                    errors={"message": "patient_id is required"},
                )
            appointment_helper: AppointmentHelper = (
                await Factory().get_appointment_helper()
            )
            response_data = await appointment_helper.create_appointment(
                patient_id,
                form_data.name,
                form_data.doctor_id,
                form_data.work_schedule_id,
                form_data.pre_examination_notes,
            )
            return response_data
        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            log.error(e)
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            ) from e
