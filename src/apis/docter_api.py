import logging as log

from regex import F

from src.core import HTTPEndpoint
from src.core.exception import BadRequest, Forbidden, InternalServer
from src.core.security import JsonWebToken
from src.enum import ErrorCode, Role
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
                elif query_params.type_of_disease == "online":
                    where["$or"] = [{"type_of_disease": "online"}, {
                        "type_of_disease": "both"}]
                else:
                    where["$or"] = [{"type_of_disease": "offline"}, {
                        "type_of_disease": "both"}]
            if query_params.key_word:
                where["$or"] = [
                    {"first_name": {"$regex": query_params.key_word}},
                    {"last_name": {"$regex": query_params.key_word}}
                ]
            if query_params.phone_number:
                where["phone_number"] = query_params.phone_number
            if query_params.is_local_person is not None:
                where["is_local_person"] = query_params.is_local_person
            response_data = await doctor_helper.get_all_doctor(current_page=current_page, page_size=page_size, where=where)

            return response_data
        except Exception as e:
            log.error(f"Error: {e}")
            raise InternalServer(msg="Internal server error",
                                 error_code=ErrorCode.SERVER_ERROR.name) from e


class GetAllDoctorLocalAPi(HTTPEndpoint):
    async def get(self, query_params: RequestGetAllDoctorsSchema, auth: JsonWebToken):
        try:
            # if auth.get("role") != Role.ADMIN.name:
            #     raise Forbidden(msg="Permission denied",
            #                     error_code=ErrorCode.FORBIDDEN.name,
            #                     errors={"message": "You don't have permission to access this resource"})
            doctor_helper: DoctorHelper = await Factory().get_doctor_helper()
            current_page = query_params.current_page if query_params.current_page else 0
            page_size = query_params.page_size if query_params.page_size else 10
            where = {"verify_status": {"$eq": 2}, "is_local_person": True}
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


class GetAllDoctorForeignAPi(HTTPEndpoint):
    async def get(self, query_params: RequestGetAllDoctorsSchema, auth: JsonWebToken):
        try:
            if auth.get("role") != Role.ADMIN.name:
                raise Forbidden(msg="Permission denied",
                                error_code=ErrorCode.FORBIDDEN.name,
                                errors={"message": "You don't have permission to access this resource"})
            doctor_helper: DoctorHelper = await Factory().get_doctor_helper()
            current_page = query_params.current_page if query_params.current_page else 0
            page_size = query_params.page_size if query_params.page_size else 10
            where = {"verify_status": {"$eq": 2}, "is_local_person": False}
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
    async def get(self, path_params: RequestDetailDoctorSchema):
        try:
            doctor_helper: DoctorHelper = await Factory().get_doctor_helper()
            reponse = await doctor_helper.get_doctor_by_id(path_params.doctor_id)
            return reponse if reponse else {"message": "Doctor not found"}
        except Exception as e:
            log.error(f"Error: {e}")
            raise InternalServer(msg="Internal server error",
                                 error_code=ErrorCode.SERVER_ERROR.name) from e


class StatisticalDoctorApi(HTTPEndpoint):
    async def get(self, auth: JsonWebToken):
        try:
            if auth.get("role") != Role.ADMIN.name:
                raise Forbidden(msg="Permission denied",
                                error_code=ErrorCode.FORBIDDEN.name,
                                errors={"message": "You don't have permission to access this resource"})

            doctor_helper: DoctorHelper = await Factory().get_doctor_helper()
            statistics = await doctor_helper.get_doctor_statistics()
            return statistics
        except Forbidden as e:
            raise e
        except Exception as e:
            log.error(f"Error in StatisticalDoctorApi: {e}")
            raise InternalServer(msg="Internal server error",
                                 error_code=ErrorCode.SERVER_ERROR.name,
                                 errors={
                                     "message": "Internal server error"
                                 }) from e
