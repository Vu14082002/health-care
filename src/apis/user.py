
import logging as log

from src.core import HTTPEndpoint
from src.core.exception import InternalServer
from src.enum import ErrorCode
from src.factory import Factory
from src.schema import RequestRegisterPatientSchema


class PatientRegisterApi(HTTPEndpoint):
    async def post(self, form_data: RequestRegisterPatientSchema):
        try:
            user_helper = await Factory().get_user_helper()
            user_saved = await user_helper.insert_user(form_data.model_dump())
            return user_saved
        except Exception as e:
            log.error("Error on PatientRegisterApi: %s", e)
            raise InternalServer(
                msg=f"An error occurred while trying to register the user: {e}",
                error_code=ErrorCode.SERVER_ERROR.name) from e
