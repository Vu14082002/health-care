import logging

from src.core.endpoint import HTTPEndpoint
from src.core.exception import BadRequest, BaseException, InternalServer
from src.core.security.authentication import JsonWebToken
from src.enum import ErrorCode, Role
from src.factory import Factory
from src.schema.rating_schema import RequestCreateRatingSchema


class RatingApi(HTTPEndpoint):

    async def post(self, form_data: RequestCreateRatingSchema, auth: JsonWebToken):
        try:
            user_role = auth.get("role")
            if user_role != Role.PATIENT.name:
                raise BadRequest(
                    error_code=ErrorCode.BAD_REQUEST.name,
                    errors={"message": ErrorCode.msg_only_support_patient.value},
                )
            user_id = auth.get("id")
            if not user_id:
                raise BadRequest(
                    error_code=ErrorCode.BAD_REQUEST.name,
                    errors={"message": "access token invalid"},
                )
            patient_helper = await Factory().get_patient_helper()
            result = await patient_helper.create_rating_helper(user_id, form_data)
            return result
        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            logging.error(f"Error: {e}")
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            ) from e
