import logging
from src.core import HTTPEndpoint
from src.core.exception import BadRequest, Forbidden, InternalServer
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
                        "message": "You do not have permission to access this resource"
                    },
                )

            patient_helper = await Factory().get_patient_helper()
            result = await patient_helper.get_all_patient(
                curent_page=query_params.curent_page, page_size=query_params.page_size
            )
            return result
        except (BadRequest, Forbidden, InternalServer) as e:
            raise e
        except Exception as e:
            logging.error(e)
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={
                    "message": "Server currently unable to handle this request,please try again later"
                },
            )
