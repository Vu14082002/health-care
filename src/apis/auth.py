import logging
from typing import Any, Dict

from sqlalchemy.exc import NoResultFound
from starlette.background import BackgroundTask
from starlette.datastructures import UploadFile
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.core import HTTPEndpoint
from src.core.exception import BadRequest, BaseException, Forbidden, InternalServer
from src.core.security.authentication import JsonWebToken
from src.enum import ErrorCode, Role, TypeOfDisease
from src.factory import Factory
from src.helper.doctor_helper import DoctorHelper
from src.helper.email_helper import send_mail_request_additional_info
from src.helper.s3_helper import S3Service
from src.helper.user_helper import UserHelper
from src.models.doctor_model import DoctorModel
from src.schema.register import (
    RequestAdminRegisterSchema,
    RequestGetAllDoctorsNotVerifySchema,
    RequestLoginSchema,
    RequestNotifyMail,
    RequestRegisterDoctorLocalSchema,
    RequestRegisterDoctorSchema,
    RequestRegisterPatientSchema,
    RequestVerifyDoctorSchema,
    RequestVerifyFinalDoctorSchema,
)


class AdminRegisterApi(HTTPEndpoint):
    async def post(self, request: Request, form_data: RequestAdminRegisterSchema):
        """
        this api is used to register admin, only admin can access
        """
        try:
            form_request = await request.form()
            if form_request.get("avatar", None):
                if isinstance(form_request.get("avatar"), UploadFile):
                    upload_file: UploadFile = form_request.get("avatar")
                    s3_service = S3Service()
                    link_avatar = await s3_service.upload_file_from_form(upload_file)
                    form_data.avatar = link_avatar
            _user_helper: UserHelper = await Factory().get_user_helper()
            _result = await _user_helper.register_admin(form_data)
            return _result
        except Exception as ex:
            if isinstance(ex, BaseException):
                raise ex
            logging.error(f"Error: {ex}")
            raise InternalServer(
                msg="Internal server error",
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            ) from ex


class AdminNotifyRegisterMail(HTTPEndpoint):

    async def post(self, form_data: RequestNotifyMail, auth: JsonWebToken):
        """
        this api is used to send mail request additional info, only admin can access
        """
        try:
            if auth.get("role", "") != Role.ADMIN.name:
                raise Forbidden(
                    error_code=ErrorCode.UNAUTHORIZED.name,
                    errors={"message": ErrorCode.msg_permission_denied.value},
                )
            task = BackgroundTask(
                send_mail_request_additional_info, form_data.email, form_data.message
            )
            return JSONResponse(
                content={"message": "Gửi thư yêu cầu thêm thông tin thành công"},
                status_code=200,
                background=task,
            )
        except Exception as ex:
            if isinstance(ex, BaseException):
                raise ex
            logging.error(f"Error: {ex}")
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            ) from ex


class PatientRegisterApi(HTTPEndpoint):
    async def post(self, form_data: RequestRegisterPatientSchema):
        """
        this api is used to register patient
        """
        try:
            avatar = None
            if isinstance(form_data.avatar, UploadFile):
                upload_file: UploadFile = form_data.avatar  # type: ignore
                s3_service = S3Service()
                await upload_file.seek(0)
                avatar = await s3_service.upload_file_from_form(upload_file)
            form_data.avatar = avatar
            _user_helper = await Factory().get_user_helper()
            _result = await _user_helper.register_patient(form_data)
            return _result
        except Exception as ex:
            if isinstance(ex, BaseException):
                raise ex
            logging.error(f"Error: {ex}")
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            ) from ex


class DoctorLocalRegisterApi(HTTPEndpoint):


    async def post(
        self, form_data: RequestRegisterDoctorLocalSchema, auth: JsonWebToken
    ):
        """
        this api is used to register doctor local, only admin can access
        """
        try:
            if auth.get("role", "") != Role.ADMIN.name:
                raise BadRequest(
                    error_code=ErrorCode.UNAUTHORIZED.name,
                    errors={"message": ErrorCode.msg_permission_denied.value},
                )
            avatar = None
            if isinstance(form_data.avatar, UploadFile):
                upload_file: UploadFile = form_data.avatar  # type: ignore
                s3_service = S3Service()
                await upload_file.seek(0)
                avatar = await s3_service.upload_file_from_form(upload_file)
            form_data.avatar = avatar
            doctor_helper = await Factory().get_doctor_helper()
            data = form_data.model_dump()
            data["verify_status"] = 2
            result: tuple[DoctorModel, BackgroundTask] = (
                await doctor_helper.create_doctor(data)
            )
            reponse = {"data": result[0].as_dict, "errors": None, "error_code": None}
            return JSONResponse(content=reponse, status_code=200, background=result[1])
        except Exception as ex:
            if isinstance(ex, BaseException):
                raise ex
            logging.error(f"Error: {ex}")
            raise InternalServer(
                msg="Internal server error",
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            ) from ex


class DoctorOtherVerifyApi(HTTPEndpoint):
    async def get(
        self, query_params: RequestGetAllDoctorsNotVerifySchema, auth: JsonWebToken
    ):
        """
        Get all doctor not verify by admin, only admin can access
        have search by key_word, verify_status and pagination
        """
        try:
            if auth.get("role") != Role.ADMIN.name:
                raise Forbidden(
                    error_code=ErrorCode.UNAUTHORIZED.name,
                    errors={
                        "message": ErrorCode.msg_permission_denied.value,
                    },
                )

            doctor_helper: DoctorHelper = await Factory().get_doctor_helper()
            current_page = query_params.current_page
            page_size = query_params.page_size
            where = {}
            if query_params.verify_status is None:
                where.update({"verify_status": {"$in": [0, 1, -1]}})
            else:
                where.update({"verify_status": query_params.verify_status})

            text_search = query_params.text_search
            response_data = await doctor_helper.get_all_doctor_by_text_search(
                current_page=current_page,
                page_size=page_size,
                text_search=text_search,
                where=where,
            )
            return response_data
        except Exception as ex:
            if isinstance(ex, BaseException):
                raise ex
            logging.error(f"Error: {ex}")
            raise InternalServer(
                msg="Internal server error",
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            ) from ex


class DoctorOtherRejectApiPut(HTTPEndpoint):
    async def put(self, path_params: RequestVerifyDoctorSchema, auth: JsonWebToken):
        '''
        this api is used to reject doctor then send mail template Reject, only admin can access
        '''
        try:
            if auth.get("role", "") != Role.ADMIN.name:
                raise Forbidden(
                    error_code=ErrorCode.UNAUTHORIZED.name,
                    errors={"message": ErrorCode.msg_permission_denied.value},
                )

            doctor_helper: DoctorHelper = await Factory().get_doctor_helper()
            result = await doctor_helper.verify_doctor(
                doctor_id=path_params.doctor_id, verify_status=-1, online_price=0
            )
            if result:
                return {"message": "Bác sĩ đã xác minh thành công ở trạng thái -1"}
            else:
                raise BadRequest(
                    error_code=ErrorCode.NOT_FOUND.name,
                    errors={"message": ErrorCode.msg_doctor_not_found_or_reject.value},
                )
        except Exception as ex:
            if isinstance(ex, BaseException):
                raise ex
            logging.error(f"Error: {ex}")
            raise InternalServer(
                msg="Internal server error",
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            ) from ex


class DoctorOtherVerifyApiPut(HTTPEndpoint):
    async def put(self, path_params: RequestVerifyDoctorSchema, auth: JsonWebToken):
        '''
        this api is used to verify doctor status 1, only admin can access
        '''
        try:
            if auth.get("role", "") != Role.ADMIN.name:
                raise Forbidden(
                    msg="Unauthorized access",
                    error_code=ErrorCode.UNAUTHORIZED.name,
                    errors={"message": "only admin can access"},
                )

            doctor_helper: DoctorHelper = await Factory().get_doctor_helper()
            result = await doctor_helper.verify_doctor(
                doctor_id=path_params.doctor_id, verify_status=1, online_price=None
            )
            if result:
                return {"message": "Bác sĩ đã xác minh thành công ở trạng thái 1"}
            else:
                raise BadRequest(
                    error_code=ErrorCode.NOT_FOUND.name,
                    errors={
                        "message": ErrorCode.msg_doctor_not_found_or_verify_status_1.value
                    },
                )
        except Exception as ex:
            if isinstance(ex, BaseException):
                raise ex
            logging.error(f"Error: {ex}")
            raise InternalServer(
                msg="Internal server error",
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            ) from ex


class DoctorForeignRegisterApi(HTTPEndpoint):
    async def post(self, form_data: RequestRegisterDoctorSchema):
        '''
        this api is used to register doctor foreign, verify_status = 0
        '''
        try:
            avatar = None
            if isinstance(form_data.avatar, UploadFile):
                upload_file: UploadFile = form_data.avatar  # type: ignore
                s3_service = S3Service()
                avatar = await s3_service.upload_file_from_form(upload_file)
            form_data.avatar = avatar
            doctor_helper = await Factory().get_doctor_helper()
            data = form_data.model_dump()
            data["verify_status"] = 0
            data["is_local_person"] = False
            data["type_of_disease"] = TypeOfDisease.ONLINE.value
            result = await doctor_helper.create_doctor(data)
            reponse = {"data": result[0].as_dict, "errors": None, "error_code": None}
            return JSONResponse(content=reponse, status_code=200, background=result[1])
        except Exception as ex:
            if isinstance(ex, BaseException):
                raise ex
            logging.error(f"Error: {ex}")
            raise InternalServer(
                msg="Internal server error",
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            ) from ex


class DoctorForeignRejectApi(HTTPEndpoint):

    async def put(self, path_params: RequestVerifyDoctorSchema, auth: JsonWebToken):
        '''
        this api is used to reject doctor then send mail template Reject, only admin can access
        '''
        try:
            if auth.get("role", "") != Role.ADMIN.name:
                raise Forbidden(
                    error_code=ErrorCode.UNAUTHORIZED.name,
                    errors={"message": ErrorCode.msg_permission_denied.value},
                )

            doctor_helper: DoctorHelper = await Factory().get_doctor_helper()
            result = await doctor_helper.reject_doctor(doctor_id=path_params.doctor_id)
            return JSONResponse(
                content=result[0], status_code=200, background=result[1]
            )
        except Exception as ex:
            if isinstance(ex, BaseException):
                raise ex
            logging.error(f"Error: {ex}")
            raise InternalServer(
                msg="Internal server error",
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            ) from ex


class LoginApi(HTTPEndpoint):
    async def post(self, form_data: RequestLoginSchema) -> Dict[str, Any]:
        try:
            user_helper: UserHelper = await Factory().get_user_helper()
            reponse_json = await user_helper.login(
                form_data.phone_number, form_data.password
            )
            return reponse_json
        except Exception as ex:
            if isinstance(ex, BaseException):
                raise ex
            logging.error(f"Error: {ex}")
            raise InternalServer(
                msg="Internal server error",
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            ) from ex


class LogoutApi(HTTPEndpoint):
    async def post(self, request: Request):
        try:
            header = request.headers.get("Authorization")
            if header:
                token = header.split(" ")[1]
                user_helper: UserHelper = await Factory().get_user_helper()
                reponse_json = await user_helper.logout(token)
                return reponse_json
            else:
                raise BadRequest(
                    error_code=ErrorCode.BAD_REQUEST.name,
                    errors={"message": ErrorCode.msg_server_error.value},
                )
        except Exception as ex:
            if isinstance(ex, BaseException):
                raise ex
            logging.error(f"Error: {ex}")
            raise InternalServer(
                msg="Internal server error",
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            ) from ex


class DoctorOtherVerifyFinalApiPut(HTTPEndpoint):
    async def put(
        self,
        form_data: RequestVerifyFinalDoctorSchema,
        auth: JsonWebToken,
    ):
        '''
        this api is used to verify doctor status 2, only admin can access
        '''
        try:
            if auth.get("role", "") != Role.ADMIN.name:
                raise Forbidden(
                    error_code=ErrorCode.UNAUTHORIZED.name,
                    errors={"message": ErrorCode.msg_permission_denied.value},
                )
            doctor_helper: DoctorHelper = await Factory().get_doctor_helper()
            result = await doctor_helper.verify_doctor(
                doctor_id=form_data.doctor_id,
                verify_status=2,
                online_price=form_data.online_price,
            )
            if result:
                return {"message": "Bác sĩ đã xác minh thành công ở trạng thái 2"}
            else:
                raise BadRequest(
                    error_code=ErrorCode.NOT_FOUND.name,
                    errors={
                        "message": ErrorCode.msg_doctor_not_found_or_verify_status_2.value
                    },
                )
        except Exception as ex:
            if isinstance(ex, BaseException):
                raise ex
            logging.error(f"Error: {ex}")
            raise InternalServer(
                msg="Internal server error",
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            ) from ex
