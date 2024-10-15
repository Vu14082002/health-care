import logging as log

from src.core import HTTPEndpoint
from src.core.exception import BadRequest, BaseException, Forbidden, InternalServer
from src.core.security import JsonWebToken
from src.enum import ErrorCode, Role
from src.factory import Factory
from src.helper.doctor_helper import DoctorHelper
from src.schema.doctor_schema import (
    RequestDetailDoctorSchema,
    RequestDoctorPatientByIdSchema,
    RequestDoctorPatientSchema,
    RequestGetAllDoctorsSchema,
)


class GetAllDoctorApi(HTTPEndpoint):
    async def get(self, query_params: RequestGetAllDoctorsSchema):
        try:
            doctor_helper: DoctorHelper = await Factory().get_doctor_helper()
            current_page = query_params.current_page if query_params.current_page else 0
            page_size = query_params.page_size if query_params.page_size else 10
            where = {"verify_status": {"$ne": 0}}
            if query_params.type_of_disease:
                if query_params.type_of_disease == "both":
                    where["$or"] = [
                        {"type_of_disease": "online"},
                        {"type_of_disease": "offline"},
                        {"type_of_disease": "both"},
                    ]
                elif query_params.type_of_disease == "online":
                    where["$or"] = [
                        {"type_of_disease": "online"},
                        {"type_of_disease": "both"},
                    ]
                else:
                    where["$or"] = [
                        {"type_of_disease": "offline"},
                        {"type_of_disease": "both"},
                    ]
            if query_params.is_local_person is not None:
                where["is_local_person"] = query_params.is_local_person
            response_data = await doctor_helper.get_all_doctor(
                current_page=current_page,
                page_size=page_size,
                where=where,
                text_search=query_params.text_search,
            )

            return response_data
        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            log.error(f"Error: {e}")
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            ) from e


class GetAllDoctorLocalAPi(HTTPEndpoint):
    async def get(self, query_params: RequestGetAllDoctorsSchema, auth: JsonWebToken):
        try:
            doctor_helper: DoctorHelper = await Factory().get_doctor_helper()
            current_page = query_params.current_page if query_params.current_page else 0
            page_size = query_params.page_size if query_params.page_size else 10
            where = {"verify_status": {"$eq": 2}, "is_local_person": True}
            if query_params.type_of_disease:
                if query_params.type_of_disease == "both":
                    where["$or"] = [
                        {"type_of_disease": "online"},
                        {"type_of_disease": "offline"},
                        {"type_of_disease": "both"},
                    ]
                else:
                    where["type_of_disease"] = query_params.type_of_disease
            response_data = await doctor_helper.get_all_doctor(
                current_page=current_page,
                page_size=page_size,
                where=where,
                text_search=query_params.text_search,
            )
            return response_data
        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            log.error(f"Error: {e}")
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            ) from e


class GetAllDoctorForeignAPi(HTTPEndpoint):
    async def get(self, query_params: RequestGetAllDoctorsSchema, auth: JsonWebToken):
        try:
            if auth.get("role") != Role.ADMIN.name:
                raise Forbidden(
                    msg="Permission denied",
                    error_code=ErrorCode.FORBIDDEN.name,
                    errors={
                        "message": ErrorCode.msg_permission_denied.value,
                    },
                )
            doctor_helper: DoctorHelper = await Factory().get_doctor_helper()
            current_page = query_params.current_page if query_params.current_page else 0
            page_size = query_params.page_size if query_params.page_size else 10
            where = {"verify_status": {"$eq": 2}, "is_local_person": False}
            if query_params.type_of_disease:
                if query_params.type_of_disease == "both":
                    where["$or"] = [
                        {"type_of_disease": "online"},
                        {"type_of_disease": "offline"},
                        {"type_of_disease": "both"},
                    ]
                else:
                    where["type_of_disease"] = query_params.type_of_disease

            response_data = await doctor_helper.get_all_doctor(
                current_page=current_page,
                page_size=page_size,
                where=where,
                text_search=query_params.text_search,
            )
            return response_data
        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            log.error(f"Error: {e}")
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            ) from e


class GetDetailtDoctorById(HTTPEndpoint):
    async def get(self, path_params: RequestDetailDoctorSchema):
        try:
            doctor_helper: DoctorHelper = await Factory().get_doctor_helper()
            reponse = await doctor_helper.get_doctor_by_id(path_params.doctor_id)
            return reponse if reponse else {"message": "Doctor not found"}
        except Exception as e:
            log.error(f"Error: {e}")
            raise InternalServer(
                msg="Internal server error", error_code=ErrorCode.SERVER_ERROR.name
            ) from e


class DoctorGetPatientsApi(HTTPEndpoint):
    async def get(self, query_params: RequestDoctorPatientSchema, auth: JsonWebToken):
        """
        this api using for get patient by doctor id if login user is doctor
        if login user is admin, can get all patient
        """
        try:
            user_role = auth.get("role")
            if user_role not in [Role.ADMIN.name, Role.DOCTOR.name]:
                raise Forbidden(
                    error_code=ErrorCode.FORBIDDEN.name,
                    errors={
                        "message": ErrorCode.msg_permission_denied.value,
                    },
                )
            if user_role == Role.DOCTOR.name:
                query_params.doctor_id = auth.get("id")
            doctor_helper: DoctorHelper = await Factory().get_doctor_helper()
            doctor_id = query_params.doctor_id
            current_page = query_params.current_page
            page_size = query_params.page_size
            status_order = query_params.status_order
            appointment_status = query_params.appointment_status
            examination_type = query_params.examination_type
            text_search = query_params.text_search

            response = await doctor_helper.get_patient_by_doctor_id(
                doctor_id=doctor_id,
                current_page=current_page,
                page_size=page_size,
                status_order=status_order,
                appointment_status=appointment_status,
                examination_type=examination_type,
                text_search=text_search,
            )
            return response
        except (BadRequest, Forbidden) as e:
            raise e
        except Exception as e:
            log.error(f"Error: {e}")
            raise InternalServer(
                msg="Internal server error", error_code=ErrorCode.SERVER_ERROR.name
            ) from e


class DoctorGetPatientsByIdApi(HTTPEndpoint):

    async def get(
        self, path_params: RequestDoctorPatientByIdSchema, auth: JsonWebToken
    ):
        try:
            user_role = auth.get("role")
            if user_role not in [Role.ADMIN.name, Role.DOCTOR.name]:
                raise Forbidden(
                    error_code=ErrorCode.FORBIDDEN.name,
                    errors={
                        "message": ErrorCode.msg_permission_denied.value,
                    },
                )
            doctor_helper: DoctorHelper = await Factory().get_doctor_helper()
            doctor_id = auth.get("id") if user_role == Role.DOCTOR.name else None
            patient_id = path_params.patient_id
            response = await doctor_helper.get_one_patient_by_doctor(
                doctor_id=doctor_id,
                patient_id=patient_id,
            )
            return response
        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            log.error(f"Error: {e}")
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            ) from e


class StatisticalDoctorApi(HTTPEndpoint):
    async def get(self, auth: JsonWebToken):
        try:
            if auth.get("role") != Role.ADMIN.name:
                raise Forbidden(
                    msg="Permission denied",
                    error_code=ErrorCode.FORBIDDEN.name,
                    errors={
                        "message": ErrorCode.msg_permission_denied.value,
                    },
                )

            doctor_helper: DoctorHelper = await Factory().get_doctor_helper()
            statistics = await doctor_helper.get_doctor_statistics()
            return statistics
        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            log.error(f"Error: {e}")
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            ) from e
