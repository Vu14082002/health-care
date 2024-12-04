import logging as log

from starlette.datastructures import URL, QueryParams
from starlette.requests import Request

from src.core import HTTPEndpoint
from src.core.exception import BadRequest, BaseException, Forbidden, InternalServer
from src.core.security.authentication import JsonWebToken
from src.enum import ErrorCode, Role
from src.factory import Factory
from src.helper.appointment_helper import AppointmentHelper
from src.schema.appointment_schema import (
    RequestDeleteAppointment,
    RequestGetAllAppointmentSchema,
    RequestRegisterAppointment,
)


class PaymentApi(HTTPEndpoint):
    async def get(self, request: Request):
        '''
        this api is used to get all appointments, only admin, doctor and patient can get all appointments
        '''
        _query_params: QueryParams =request.query_params
        payment_id = _query_params.get("id")
        if not payment_id:
            raise BadRequest(
                error_code=ErrorCode.BAD_REQUEST.name,
                errors={"message":"payment_id is required"}
            )
        status_code = _query_params.get("code", "")

        appointment_helper = await Factory().get_appointment_helper()

        _data = await appointment_helper.create_appointment_with_payment(
            payment_id=payment_id, status_code=status_code
        )

        return _data

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
    async def post(self, request:Request,form_data: RequestRegisterAppointment, auth: JsonWebToken):
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
            return_url: URL = request.url
            call_back_url: str = f"{return_url.scheme}://{return_url.netloc}/payment-appointment"
            response_data = await appointment_helper.create_appointment(
                patient_id=patient_id,
                name=form_data.name,
                doctor_id=form_data.doctor_id,
                work_schedule_id=form_data.work_schedule_id,
                pre_examination_notes=form_data.pre_examination_notes,
                is_payment=form_data.is_payment,
                call_back_url=call_back_url,
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

    async def delete(self,form_data:RequestDeleteAppointment,auth:JsonWebToken):
        '''
        this api for patient delele appointment
        '''
        user_role = auth.get("role")
        if user_role not in [Role.ADMIN.value,Role.PATIENT.value]:
            raise Forbidden(
                error_code=ErrorCode.FORBIDDEN.name,
                errors={
                    "message":ErrorCode.msg_permission_denied.value
                }
            )
        if user_role is Role.ADMIN.value and not form_data.patient_id:
            raise BadRequest(
                error_code=ErrorCode.BAD_REQUEST.name,
                errors={
                    "message":ErrorCode.msg_patient_id_is_required.value
                }
            )
        patient_id = (
            form_data.patient_id
            if user_role is Role.ADMIN.value
            else auth.get("id")
        )
        appointment_id = form_data.appointment_id
        appointment_helper = await Factory().get_appointment_helper()
        result =await appointment_helper.delete_appointment(appointment_id, patient_id)
        return result
