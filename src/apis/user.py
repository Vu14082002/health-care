import logging

from starlette.datastructures import UploadFile

from src.core import HTTPEndpoint
from src.core.exception import BadRequest, BaseException, InternalServer
from src.core.security.authentication import JsonWebToken
from src.enum import ErrorCode, Role
from src.factory import Factory
from src.helper.s3_helper import S3Service
from src.schema.register import (
    RequestRegisterPatientSchema,
    RequestResetPasswordSchema,
    RequestUpdateUserSchema,
)


class PatientRegisterApi(HTTPEndpoint):
    async def post(self, form_data: RequestRegisterPatientSchema):
        try:
            user_helper = await Factory().get_user_helper()
            user_saved = await user_helper.insert_user(form_data.model_dump())
            return user_saved
        except Exception as e:
            logging.error("Error on PatientRegisterApi: %s", e)
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
            if form_data.avatar:
                if isinstance(form_data.avatar, UploadFile):
                    upload_file: UploadFile = form_data.avatar  # type: ignore
                    s3_service = S3Service()
                    await upload_file.seek(0)
                    avatar = await s3_service.upload_file_from_form(upload_file)
                    form_data.avatar = avatar
            user_saved = await user_helper.update_profile(
                user_id=auth.get("id"), data=form_data.model_dump()
            )
            return user_saved
        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            logging.error(f"Error: {e}")
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            ) from e


class ResetPassword(HTTPEndpoint):
    async def put(self, form_data: RequestResetPasswordSchema, auth: JsonWebToken):
        try:
            user_helper = await Factory().get_user_helper()
            user_saved = await user_helper.reset_pwd(
                user_id=auth.get("id"),
                phone_number=auth.get("phone_number"),
                password=form_data.password,
                old_password=form_data.old_password,
            )
            return user_saved
        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            logging.error(f"Error: {e}")
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            ) from e
