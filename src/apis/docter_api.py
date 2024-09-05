import logging as log

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
                                      RequestUpdateDoctorSchema,
                                      RequestUpdatePathParamsSchema)


class GetAllDoctorApi(HTTPEndpoint):
    async def get(self, query_params: RequestGetAllDoctorsSchema, auth: JsonWebToken):
        try:
            doctor_helper: DoctorHelper = await Factory().get_doctor_helper()
            current_page = query_params.current_page if query_params.current_page else 0
            page_size = query_params.page_size if query_params.page_size else 10
            where = {}
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
        try:
            role: str = auth["role"] if auth["role"] else ""  # type: ignore
            id_login: str = auth["id"] if auth["id"] else ""  # type: ignore
            if role != "ADMIN" or (id_login != path_params.doctor_id and role == "DOCTOR"):
                raise Forbidden(msg="Forbidden",
                                error_code=ErrorCode.FORBIDDEN.name, errors={"message": "You don't have permission to access"})
            doctor_helper: DoctorHelper = await Factory().get_doctor_helper()
            reponse = await doctor_helper.update_doctor(path_params.doctor_id, form_data.model_dump())
            return reponse.as_dict if reponse else {"message": f"Doctor with id: {path_params.doctor_id} not found"}
        except Forbidden as e:
            raise e
        except Exception as e:
            log.error(f"Error: {e}")
            raise InternalServer(msg="Internal server error",
                                 error_code=ErrorCode.SERVER_ERROR.name) from e


class DoctorWorkingTimeApi(HTTPEndpoint):

    async def get(self, auth: JsonWebToken):
        return {"message": "Get doctor working time"}

    async def post(self, form_data: RequestDoctorWorkScheduleNextWeek, auth: JsonWebToken):
        try:
            if auth.get("role", "") != "DOCTOR":
                raise Forbidden(msg="Forbidden",
                                error_code=ErrorCode.FORBIDDEN.name,
                                errors={"message": "Only doctors can access this endpoint"})

            doctor_helper: DoctorHelper = await Factory().get_doctor_helper()
            response = await doctor_helper.create_doctor_work_schedule(doctor_id=auth.get("id"), data=form_data)
            return response
        except Forbidden as e:
            raise
        except Exception as e:
            log.error(f"Error creating doctor work schedule: {e}")
            raise InternalServer(msg="Internal server error",
                                 error_code=ErrorCode.SERVER_ERROR.name) from e
