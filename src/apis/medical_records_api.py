import logging as log

from regex import R

from src.core import HTTPEndpoint
from src.core.exception import BadRequest, Forbidden, InternalServer
from src.core.security.authentication import JsonWebToken
from src.enum import ErrorCode, Role
from src.factory import Factory
from src.schema.medical_records_schema import (
    RequestCreateMedicalRecordsSchema, RequestGetAllMedicalRecordsSchema)


class MedicalRecordsApiGET(HTTPEndpoint):
    async def get(self, auth: JsonWebToken):
        # try:
        #     medical_records_helper = await Factory().get_medical_records_helper()
        #     user_role = auth.get("role", "")
        #     user_id = auth.get("id")

        #     if user_role not in [Role.ADMIN.value, Role.DOCTOR.value, Role.PATIENT.value]:
        #         raise Forbidden(msg="Unauthorized access",
        #                         error_code=ErrorCode.UNAUTHORIZED.name)

        #     filter_params = query_params.model_dump()
        #     medical_records = {}
        #     if user_role == Role.ADMIN.value:
        #         medical_records = await medical_records_helper.get_all_medical_records(**filter_params)
        #     elif user_role == Role.DOCTOR.value:
        #         # Doctor can only see their own medical_records
        #         filter_params["doctor_id"] = user_id
        #         medical_records = await medical_records_helper.get_all_medical_records(**filter_params)
        #     elif user_role == Role.PATIENT.value:
        #         filter_params["patient_id"] = user_id
        #         medical_records = await medical_records_helper.get_all_medical_records(**filter_params)
        #     return medical_records
        # except Forbidden as e:
        #     log.error(e)
        #     raise e
        # except Exception as e:
        #     log.error(e)
        #     raise InternalServer(msg="Internal server error",
        #                          error_code=ErrorCode.SERVER_ERROR.name, errors={"message": "server is error, please try later"}) from e
        return {"message": "this is not implemented yet"}


class MedicalRecordsApiPOST(HTTPEndpoint):
    async def post(self, form_data: RequestCreateMedicalRecordsSchema, auth: JsonWebToken):
        try:
            user_role = auth.get("role", "")
            if user_role not in [Role.DOCTOR.name, Role.ADMIN.name]:
                raise Forbidden(msg="Unauthorized access",
                                error_code=ErrorCode.UNAUTHORIZED.name, errors={"message": "You are not authorized to access this resource"})
            if user_role == Role.ADMIN.name and form_data.doctor_id is None:
                raise BadRequest(msg="Bad request",
                                 error_code=ErrorCode.BAD_REQUEST.name, errors={"message": "Doctor id is required"})
            form_data.doctor_id = auth.get(
                "id") if user_role == Role.DOCTOR.name else form_data.doctor_id
            medical_records_helper = await Factory().get_medical_records_helper()
            result = await medical_records_helper.create_medical_records(value=form_data)
            return result
        except (BadRequest, Forbidden, InternalServer) as e:
            log.error(e)
            raise e
        except Exception as e:
            log.error(e)
            raise InternalServer(msg="Internal server error",
                                 error_code=ErrorCode.SERVER_ERROR.name, errors={"message": "server is error, please try later"}) from e
