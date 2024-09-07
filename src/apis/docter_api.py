import logging as log

from src.core import HTTPEndpoint
from src.core.exception import BadRequest, Forbidden, InternalServer
from src.core.security import JsonWebToken
from src.enum import ErrorCode
from src.factory import Factory
from src.helper.doctor_helper import DoctorHelper
from src.schema.doctor_schema import (RequestDetailDoctorSchema,
                                      RequestDoctorWorkScheduleNextWeek,
                                      RequestGetAllDoctorsSchema,
                                      RequestGetUncenteredTimeSchema,
                                      RequestGetWorkingTimeSchema,
                                      RequestUpdateDoctorSchema,
                                      RequestUpdatePathParamsSchema)


class GetAllDoctorApi(HTTPEndpoint):
    async def get(self, query_params: RequestGetAllDoctorsSchema):
        try:
            doctor_helper: DoctorHelper = await Factory().get_doctor_helper()
            current_page = query_params.current_page if query_params.current_page else 0
            page_size = query_params.page_size if query_params.page_size else 10
            where = {"verify_status": {"$ne": 0}}
            if query_params.type_of_disease:
                if query_params.type_of_disease == "both":
                    where["$or"] = [{"type_of_disease": "online"}, {
                        "type_of_disease": "offline"}, {"type_of_disease": "both"}]
                else:
                    where["type_of_disease"] = query_params.type_of_disease
            if query_params.key_word:
                where["$or"] = [
                    {"first_name": {"$regex": query_params.key_word}},
                    {"last_name": {"$regex": query_params.key_word}}
                ]
            if query_params.phone_number:
                where["phone_number"] = query_params.phone_number
            response_data = await doctor_helper.get_all_doctor(current_page=current_page, page_size=page_size, where=where)
            return response_data
        except Exception as e:
            log.error(f"Error: {e}")
            raise InternalServer(msg="Internal server error",
                                 error_code=ErrorCode.SERVER_ERROR.name) from e


class GetDetailtDoctorById(HTTPEndpoint):
    async def get(self, path_params: RequestDetailDoctorSchema, auth: JsonWebToken):
        try:
            doctor_helper: DoctorHelper = await Factory().get_doctor_helper()
            reponse = await doctor_helper.get_doctor_by_id(path_params.doctor_id)
            return reponse if reponse else {"message": "Doctor not found"}
        except Exception as e:
            log.error(f"Error: {e}")
            raise InternalServer(msg="Internal server error",
                                 error_code=ErrorCode.SERVER_ERROR.name) from e


class DoctorWorkingTimeApi(HTTPEndpoint):
    async def get(self, query_params: RequestGetWorkingTimeSchema, auth: JsonWebToken):
        try:
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
            if role not in ["DOCTOR", "ADMIN"]:
                raise Forbidden(
                    "Only doctors or Admin can access this endpoint")

            doctor_id = auth.get(
                "id") if role == "DOCTOR" else form_data.doctor_id
            if not doctor_id:
                raise BadRequest("Doctor id is required")

            if role == "DOCTOR":
                verify_status = auth.get("verify_status")
                if verify_status not in [1, 2]:
                    raise Forbidden(
                        "Only doctors with verify_status = 1 or 2 can add working schedule")
                if verify_status != 2 and form_data.examination_type == "offline":
                    raise Forbidden(
                        "Only doctors with verify_status = 2 can add offline working schedule")
            doctor_helper: DoctorHelper = await Factory().get_doctor_helper()
            return await doctor_helper.create_doctor_work_schedule(doctor_id=doctor_id, data=form_data)
        except (Forbidden, BadRequest) as e:
            raise e
        except Exception as e:
            log.error(f"Error creating doctor work schedule: {e}")
            raise


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
