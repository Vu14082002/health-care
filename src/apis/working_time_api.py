import logging

from src.core import HTTPEndpoint
from src.core.exception import BadRequest, BaseException, Forbidden, InternalServer
from src.core.security import JsonWebToken
from src.enum import ErrorCode, Role
from src.factory import Factory
from src.helper.doctor_helper import DoctorHelper
from src.schema.doctor_schema import (
    RequestDoctorWorkScheduleNextWeek,
    RequestGetUncenteredTimeSchema,
    RequestGetWorkingTimeByIdSchema,
    RequestGetWorkingTimeOrderedSchema,
    RequestGetWorkingTimeSchema,
)


class DoctorWorkingTimeApi(HTTPEndpoint):
    async def get(self, query_params: RequestGetWorkingTimeSchema, auth: JsonWebToken):
        try:
            user_role = auth.get("role")
            query_params.ordered = (
                False
                if user_role not in [Role.ADMIN.name, Role.DOCTOR.name]
                else query_params.ordered
            )
            doctor_helper: DoctorHelper = await Factory().get_doctor_helper()
            response = await doctor_helper.get_working_schedules(
                **query_params.model_dump()
            )
            return response
        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            logging.error(f"Error: {e}")
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            ) from e


class DoctorWorkingTimeByIdApi(HTTPEndpoint):
    async def get(
        self, path_params: RequestGetWorkingTimeByIdSchema, auth: JsonWebToken
    ):
        try:
            doctor_helper: DoctorHelper = await Factory().get_doctor_helper()
            response = await doctor_helper.get_working_schedules_by_id(
                id=path_params.id
            )
            return response
        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            logging.error(f"Error: {e}")
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            ) from e


class DoctorWorkingTimeOrderedApi(HTTPEndpoint):
    async def get(
        self, query_params: RequestGetWorkingTimeOrderedSchema, auth: JsonWebToken
    ):
        try:

            where = query_params.model_dump()
            patient_id = (
                auth.get("id") if auth.get("role") == Role.PATIENT.name else None
            )
            where["patient_id"] = patient_id

            doctor_id = auth.get("id") if auth.get("role") == "DOCTOR" else None
            where = {}
            doctor_helper: DoctorHelper = await Factory().get_doctor_helper()
            response = await doctor_helper.get_working_schedules(
                **query_params.model_dump()
            )
            return response
        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            logging.error(f"Error: {e}")
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            ) from e


class CreateDoctorWorkingTimeApi(HTTPEndpoint):
    async def post(
        self, form_data: RequestDoctorWorkScheduleNextWeek, auth: JsonWebToken
    ):
        try:
            role = auth.get("role", "")
            if role not in [Role.DOCTOR.name, Role.ADMIN.name]:
                raise Forbidden(
                    error_code=ErrorCode.FORBIDDEN.name,
                    errors={"message": "You can't access this endpoint"},
                )

            doctor_id = (
                auth.get("id") if role == Role.DOCTOR.name else form_data.doctor_id
            )
            if not doctor_id:
                raise BadRequest(
                    error_code=ErrorCode.BAD_REQUEST.name,
                    errors={"message": "Doctor id is required"},
                )
            doctor_helper: DoctorHelper = await Factory().get_doctor_helper()
            return await doctor_helper.create_doctor_work_schedule(
                doctor_id=doctor_id, data=form_data
            )

        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            logging.error(f"Error: {e}")
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            ) from e


class DoctorEmptyWorkingSchedulingTimeApi(HTTPEndpoint):
    async def get(
        self, query_params: RequestGetUncenteredTimeSchema, auth: JsonWebToken
    ):
        try:

            user_role = auth.get("role")
            user_id = auth.get("id")
            if user_role not in [Role.DOCTOR.name, Role.ADMIN.name]:
                raise Forbidden(
                    msg="Forbidden",
                    error_code=ErrorCode.FORBIDDEN.name,
                    errors={
                        "message": "Only doctors or Admin can access this endpoint"
                    },
                )
            if user_role == Role.DOCTOR.name and query_params.doctor_id is not None:
                raise Forbidden(
                    msg="Forbidden",
                    error_code=ErrorCode.FORBIDDEN.name,
                    errors={"message": "You are not allowed to access this endpoint"},
                )
            doctor_id = (
                user_id if user_role == Role.DOCTOR.name else query_params.doctor_id
            )
            if doctor_id is None:
                raise BadRequest(
                    msg="Bad Request",
                    error_code=ErrorCode.BAD_REQUEST.name,
                    errors={"message": "Doctor id is required"},
                )
            doctor_helper: DoctorHelper = await Factory().get_doctor_helper()
            response = await doctor_helper.get_empty_working_time(
                doctor_id=doctor_id,
                start_date=query_params.start_date,
                end_date=query_params.end_date,
            )
            return response
        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            logging.error(f"Error: {e}")
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            ) from e
