import logging as log
from os import error

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from src.core import HTTPEndpoint
from src.core.exception import Forbidden, InternalServer
from src.core.security import JsonWebToken
from src.enum import ErrorCode
from src.factory import Factory
from src.helper.doctor_helper import DoctorHelper
from src.schema.doctor_schema import (RequestDetailDoctorSchema,
                                      RequestDoctorWorkScheduleNextWeek,
                                      RequestGetAllDoctorsSchema,
                                      RequestGetUncenteredTimeSchema,
                                      RequestGetWorkingSchedulesSchema,
                                      RequestUpdateDoctorSchema,
                                      RequestUpdatePathParamsSchema)


class GetAllDoctorApi(HTTPEndpoint):
    async def get(self, query_params: RequestGetAllDoctorsSchema, auth: JsonWebToken):
        try:
            doctor_helper: DoctorHelper = await Factory().get_doctor_helper()
            current_page = query_params.current_page if query_params.current_page else 0
            page_size = query_params.page_size if query_params.page_size else 10
            where = {"verify_status": {"$ne": 0}}
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

    async def put(self, form_data: RequestUpdateDoctorSchema, path_params: RequestUpdatePathParamsSchema, auth: JsonWebToken):
        # try:
        #     role: str = auth["role"] if auth["role"] else ""  # type: ignore
        #     id_login: str = auth["id"] if auth["id"] else ""  # type: ignore
        #     if role != "ADMIN" or (id_login != path_params.doctor_id and role == "DOCTOR"):
        #         raise Forbidden(msg="Forbidden",
        #                         error_code=ErrorCode.FORBIDDEN.name, errors={"message": "You don't have permission to access"})
        #     doctor_helper: DoctorHelper = await Factory().get_doctor_helper()
        #     reponse = await doctor_helper.update_doctor(path_params.doctor_id, form_data.model_dump())
        #     return reponse.as_dict if reponse else {"message": f"Doctor with id: {path_params.doctor_id} not found"}
        # except Forbidden as e:
        #     raise e
        # except Exception as e:
        #     log.error(f"Error: {e}")
        #     raise InternalServer(msg="Internal server error",
        #                          error_code=ErrorCode.SERVER_ERROR.name) from e
        return {"message": "Not implemented"}


class DoctorWorkingTimeApi(HTTPEndpoint):
    async def get(self,  query_params: RequestGetWorkingSchedulesSchema, auth: JsonWebToken,):
        try:
            if auth.get("role", "") != "DOCTOR":
                raise Forbidden(msg="Forbidden",
                                error_code=ErrorCode.FORBIDDEN.name,
                                errors={"message": "Only doctors can access this endpoint"})
            doctor_helper: DoctorHelper = await Factory().get_doctor_helper()
            response = await doctor_helper.get_working_schedules(doctor_id=auth.get("id"), start_date=query_params.start_date, end_date=query_params.end_date, examination_type=query_params.examination_type)
            return response
        except Forbidden as e:
            raise
        except Exception as e:
            log.error(f"Error getting doctor working schedules: {e}")
            raise InternalServer(msg="Internal server error",
                                 error_code=ErrorCode.SERVER_ERROR.name) from e

    async def post(self, form_data: RequestDoctorWorkScheduleNextWeek, auth: JsonWebToken):
        try:
            if auth.get("role", "") != "DOCTOR":
                raise Forbidden(msg="Forbidden",
                                error_code=ErrorCode.FORBIDDEN.name,
                                errors={"message": "Only doctors can access this endpoint"})
            if auth.get("verify_status") != 2 and form_data.examination_type == "offline":
                raise Forbidden(msg="Forbidden",
                                error_code=ErrorCode.FORBIDDEN.name,
                                errors={"message": "Only doctors with verify_status = 2 can access this add offline working schedule"})
            doctor_helper: DoctorHelper = await Factory().get_doctor_helper()
            response = await doctor_helper.create_doctor_work_schedule(doctor_id=auth.get("id"), data=form_data)
            return response
        except Forbidden as e:
            raise
        except Exception as e:
            log.error(f"Error creating doctor work schedule: {e}")
            raise InternalServer(msg="Internal server error",
                                 error_code=ErrorCode.SERVER_ERROR.name)


class DoctorEmptyWorkingSchedulingTimeApi(HTTPEndpoint):
    # async def get(self, query_params: RequestGetUncenteredTimeSchema, auth: JsonWebToken):
    async def get(self, auth: JsonWebToken):
        data = auth
    # try:
    #     if auth.get("role", "") not in ["DOCTOR"]:
    #         raise Forbidden(msg="Forbidden",
    #                         error_code=ErrorCode.FORBIDDEN.name,
    #                         errors={"message": "Only doctors can access this endpoint"})
    #     doctor_helper: DoctorHelper = await Factory().get_doctor_helper()
    #     id = auth.get("id")
    #     response = await doctor_helper.get_uncentered_time(doctor_id=id, start_date=query_params.start_date, end_date=query_params.end_date)
    #     return response
    # except Forbidden as e:
    #     raise e
    # except Exception as e:
    #     log.error(f"Error getting doctor empty working  time: {e}")
    #     raise InternalServer(msg="Internal server error",
    #                          error_code=ErrorCode.SERVER_ERROR.name, errors={"message": f"Error getting doctor empty working  time: {e}"}) from e
        return {"message": "Not implemented"}
