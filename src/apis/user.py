import logging as log

from src.core import HTTPEndpoint
from src.core.exception import BadRequest, InternalServer
from src.core.security.authentication import JsonWebToken
from src.enum import ErrorCode, Role
from src.factory import Factory
from src.schema.register import RequestRegisterPatientSchema, RequestUpdateUserSchema


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
                error_code=ErrorCode.SERVER_ERROR.name,
            ) from e


class UserProfile(HTTPEndpoint):

    async def put(self, form_data: RequestUpdateUserSchema, auth: JsonWebToken):
        try:
            if auth.get("role") == Role.ADMIN.value:
                return {"msg": "not implemented yet "}
            user_helper = await Factory().get_user_helper()
            user_saved = await user_helper.update_profile(
                user_id=auth.get("id"), data=form_data.model_dump()
            )
            return user_saved
        except (BadRequest, InternalServer) as e:
            raise e
        except Exception as e:
            log.error("Error on PatientRegisterApi: %s", e)
            raise InternalServer(
                msg=f"An error occurred while trying to register the user: {e}",
                error_code=ErrorCode.SERVER_ERROR.name,
            ) from e
