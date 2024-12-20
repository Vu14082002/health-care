import logging as log
from datetime import datetime, time

from src.core import HTTPEndpoint
from src.core.exception import BadRequest, BaseException, Forbidden, InternalServer
from src.core.security.authentication import JsonWebToken
from src.enum import ErrorCode, Role
from src.factory import Factory
from src.schema.medical_records_schema import (
    RequestCreateMedicalRecordsSchema,
    RequestGetAllMedicalRecordsSchema,
    RequestGetAppointmentByIdSchema,
    RequestUpdateMedicalRecordsSchema,
)


class MedicalRecordsApiGET(HTTPEndpoint):
    async def get(
        self, query_params: RequestGetAllMedicalRecordsSchema, auth: JsonWebToken
    ):
        try:
            user_role = auth.get("role", "")
            user_id = auth.get("id")
            current_page = query_params.current_page
            page_size = query_params.page_size
            where = {}
            time_unix_start = (
                int(
                    datetime.combine(
                        query_params.start_date,
                        time(
                            0,
                            0,
                            0,
                        ),
                    ).timestamp()
                )
                if query_params.start_date
                else None
            )
            time_unix_end = (
                int(
                    datetime.combine(
                        query_params.end_date,
                        time(
                            0,
                            0,
                            0,
                        ),
                    ).timestamp()
                )
                if query_params.start_date
                else None
            )

            if time_unix_start and time_unix_end:
                where["$and"] = [
                    {"created_at": {"$gte": time_unix_start}},
                    {"created_at": {"$lte": time_unix_end}},
                ]
            elif time_unix_start:
                where["created_at"] = {"$gte": query_params.start_date}
            elif time_unix_end:
                where["created_at"] = {"$lte": query_params.end_date}
            if user_role == Role.DOCTOR.value:
                where["doctor_read_id"] = user_id
            elif user_role == Role.PATIENT.value:
                where["patient_id"] = user_id
            order_by = {"created_at": "desc"}

            medical_records_helper = await Factory().get_medical_records_helper()
            result = await medical_records_helper.get_all_medical_records(
                current_page, page_size, where=where, order_by=order_by
            )
            return result
        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            log.error(f"Error: {e}")
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            ) from e


class GetMedicalRecordByAppointId(HTTPEndpoint):
    async def get(
        self, path_params: RequestGetAppointmentByIdSchema, auth: JsonWebToken
    ):
        '''
        this api is used to get medical record by appointment id, only admin, patient and doctor can get medical record
        '''
        try:
            user_role = auth.get("role", "")
            if user_role not in ["ADMIN", "PATIENT", "DOCTOR"]:
                raise Forbidden(
                    msg="Unauthorized access",
                    error_code=ErrorCode.UNAUTHORIZED.name,
                    errors={
                        "message": ErrorCode.msg_permission_denied.value,
                    },
                )
            user_id = auth.get("id")
            id = path_params.appointment_id

            helper = await Factory().get_medical_records_helper()
            result = await helper.get_medical_record_by_appointment_id(
                user_id=user_id,
                appointment_id=id,
                role=user_role,
            )
            return result
        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            log.error(f"Error: {e}")
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            ) from e


class MedicalRecordsApiPOST(HTTPEndpoint):
    async def post(
        self, form_data: RequestCreateMedicalRecordsSchema, auth: JsonWebToken
    ):
        try:
            user_role = auth.get("role", "")
            user_id = auth.get("id")
            if user_role != Role.DOCTOR.value:
                raise Forbidden(
                    msg="Unauthorized access",
                    error_code=ErrorCode.UNAUTHORIZED.name,
                    errors={
                        "message": ErrorCode.msg_permission_denied.value,
                    },
                )

            value = form_data.model_dump()
            value.update({"doctor_create_id": user_id})
            value.update({"doctor_read_id": user_id})
            medical_records_helper = await Factory().get_medical_records_helper()
            result = await medical_records_helper.create_medical_records(value=value)
            return result
        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            log.error(f"Error: {e}")
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            ) from e

    async def put(
        self, form_data: RequestUpdateMedicalRecordsSchema, auth: JsonWebToken
    ):
        try:
            user_role = auth.get("role", "")
            user_id = auth.get("id")
            if user_role != Role.DOCTOR.value:
                raise Forbidden(
                    msg="Unauthorized access",
                    error_code=ErrorCode.UNAUTHORIZED.name,
                    errors={
                        "message": ErrorCode.msg_permission_denied.value,
                    },
                )

            value = form_data.model_dump()
            value.update({"doctor_create_id": user_id})
            value.update({"doctor_read_id": user_id})
            medical_records_helper = await Factory().get_medical_records_helper()
            result = await medical_records_helper.update_medical_records(value=value)
            return result
        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            log.error(f"Error: {e}")
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            ) from e
