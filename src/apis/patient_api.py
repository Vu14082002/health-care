import logging

from src.core import HTTPEndpoint
from src.core.exception import BadRequest, BaseException, Forbidden, InternalServer
from src.core.security.authentication import JsonWebToken
from src.enum import ErrorCode, Role
from src.factory import Factory
from src.schema.patient_schema import RequestGetAllPatientSchema


class PatientApi(HTTPEndpoint):
    async def get(self, query_params: RequestGetAllPatientSchema, auth: JsonWebToken):
        """
        Get all patient by role ADMIN
        """
        try:
            if auth.get("role") != Role.ADMIN.name:
                raise Forbidden(
                    error_code=ErrorCode.FORBIDDEN.name,
                    errors={
                        "message": ErrorCode.msg_permission_denied.value,
                    },
                )

            patient_helper = await Factory().get_patient_helper()
            result = await patient_helper.get_all_patient(
                curent_page=query_params.current_page, page_size=query_params.page_size
            )
            return result
        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            logging.error(f"Error: {e}")
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            ) from e
