import logging as log

from src.core import HTTPEndpoint
from src.core.exception import InternalServer
from src.core.security import JsonWebToken
from src.enum import ErrorCode
from src.factory import Factory
from src.helper.doctor_helper import DoctorHelper
from src.schema import RequestRegisterPatientSchema
from src.schema.doctor_schema import RequestGetAllDoctorsSchema


class DoctorApi(HTTPEndpoint):
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
            return {**response_data.model_dump()}
        except Exception as e:
            log.error(f"Error: {e}")
            raise InternalServer(msg="Internal server error",
                                 error_code=ErrorCode.SERVER_ERROR.name) from e


class DockerGelAllApi(HTTPEndpoint):
    async def get(self, query_params: RequestGetAllDoctorsSchema, auth: JsonWebToken):
        try:
            doctor_helper: DoctorHelper = await Factory().get_doctor_helper()
            current_page = query_params.current_page if query_params.current_page else 0
            page_size = query_params.page_size if query_params.page_size else 10
            response_data = await doctor_helper.get_all_doctor(current_page, page_size)
            return {**response_data.model_dump()}
        except Exception as e:
            log.error(f"Error: {e}")
            raise InternalServer(msg="Internal server error",
                                 error_code=ErrorCode.SERVER_ERROR.name) from e
