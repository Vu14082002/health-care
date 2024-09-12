
import logging as log
from re import A

from src.core import HTTPEndpoint
from src.core.exception import BadRequest, Forbidden, InternalServer
from src.core.security import JsonWebToken
from src.enum import ErrorCode, Role
from src.factory import Factory
from src.helper.doctor_helper import DoctorHelper
from src.schema.doctor_schema import (RequestDoctorWorkScheduleNextWeek,
                                      RequestGetUncenteredTimeSchema,
                                      RequestGetWorkingTimeSchema)


class DoctorWorkingTimeApi(HTTPEndpoint):
    async def get(self, query_params: RequestGetWorkingTimeSchema, auth: JsonWebToken):
        try:
            if auth.get("role") == Role.PATIENT.name:
                query_params.ordered = False
            doctor_helper: DoctorHelper = await Factory().get_doctor_helper()
            id = auth.get("id") if auth.get(
                "role") == "DOCTOR" else query_params.doctor_id
            if id is None:
                raise BadRequest(msg="Forbidden",
                                 error_code=ErrorCode.FORBIDDEN.name,
                                 errors={"message": "Doctor id  is required"})
            response = await doctor_helper.get_working_schedules(**query_params.model_dump())
            return response
        except Forbidden as e:
            raise e
        except BadRequest as e:
            raise e
        except Exception as e:
            log.error(f"Error getting doctor empty working  time: {e}")
            raise InternalServer(msg="Internal server error",
                                 error_code=ErrorCode.SERVER_ERROR.name, errors={"message": f"Error getting doctor empty working  time: {e}"}) from e


class CreateDoctorWorkingTimeApi(HTTPEndpoint):

    async def post(self, form_data: RequestDoctorWorkScheduleNextWeek, auth: JsonWebToken):
        try:
            role = auth.get("role", "")
            if role not in [Role.DOCTOR.name, Role.ADMIN.name]:
                raise Forbidden(
                    error_code=ErrorCode.FORBIDDEN.name,
                    errors={
                        "message": "Only doctors or Admin can access this endpoint"}
                )

            doctor_id = auth.get(
                "id") if role == Role.DOCTOR.name else form_data.doctor_id
            if not doctor_id:
                raise BadRequest(error_code=ErrorCode.BAD_REQUEST.name, errors={
                                 "message": "Doctor id is required"})
            doctor_helper: DoctorHelper = await Factory().get_doctor_helper()
            return await doctor_helper.create_doctor_work_schedule(doctor_id=doctor_id, data=form_data)

        except (Forbidden, BadRequest) as e:
            raise e
        except Exception as e:
            log.error(f"Error creating doctor work schedule: {e}")
            raise InternalServer(msg="Internal server error",
                                 error_code=ErrorCode.SERVER_ERROR.name,
                                 errors={"message": f"Error creating doctor work schedule: {e}"}) from e


class DoctorEmptyWorkingSchedulingTimeApi(HTTPEndpoint):
    async def get(self, query_params: RequestGetUncenteredTimeSchema, auth: JsonWebToken):
        try:
            if auth.get("role", "") not in ["DOCTOR", "ADMIN"]:
                raise Forbidden(msg="Forbidden",
                                error_code=ErrorCode.FORBIDDEN.name,
                                errors={"message": "Only doctors or Admin can access this endpoint"})
            doctor_helper: DoctorHelper = await Factory().get_doctor_helper()
            doctor_id = auth.get("id") if auth.get(
                "role") == "DOCTOR" else query_params.doctor_id
            if doctor_id is None:
                raise BadRequest(msg="Bad Request",
                                 error_code=ErrorCode.BAD_REQUEST.name,
                                 errors={"message": "Doctor id is required"})
            response = await doctor_helper.get_empty_working_time(doctor_id=doctor_id, start_date=query_params.start_date, end_date=query_params.end_date)
            return response
        except Forbidden as e:
            raise e
        except BadRequest as e:
            raise e
        except Exception as e:
            log.error(f"Error getting doctor empty working time: {e}")
            raise InternalServer(msg="Internal server error",
                                 error_code=ErrorCode.SERVER_ERROR.name, errors={"message": f"Error getting doctor empty working time: {e}"}) from e
