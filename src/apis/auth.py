import logging as log
from typing import Any, Dict

from sqlalchemy.exc import NoResultFound
from starlette.background import BackgroundTask
from starlette.datastructures import UploadFile
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.core import HTTPEndpoint
from src.core.exception import BadRequest, Forbidden, InternalServer
from src.core.security.authentication import JsonWebToken
from src.enum import ErrorCode, Role, TypeOfDisease
from src.factory import Factory
from src.helper.doctor_helper import DoctorHelper
from src.helper.email_helper import send_mail_request_additional_info
from src.helper.patient_helper import PatientHelper
from src.helper.s3_helper import S3Service
from src.helper.user_repository import UserHelper
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
)


class AdminRegisterApi(HTTPEndpoint):
    async def post(self, request: Request, form_data: RequestAdminRegisterSchema):
        """
        This function is used to register admin
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
        except (BadRequest, InternalServer) as e:
            log.error(f"Error: {e}")
            raise e
        except Exception as ex:
            log.error(f"Error: {ex}")
            raise InternalServer(
                msg="Internal server error",
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.name},
            ) from ex


class AdminNotifyRegisterMail(HTTPEndpoint):

    async def post(self, form_data: RequestNotifyMail, auth: JsonWebToken):
        """
        This function is used to request notify mail
        """
        if auth.get("role", "") != Role.ADMIN.name:
            raise Forbidden(
                msg="Unauthorized access",
                error_code=ErrorCode.UNAUTHORIZED.name,
                errors={"message": ErrorCode.msg_permission_denied.value},
            )
        task = BackgroundTask(
            send_mail_request_additional_info, form_data.email, form_data.message
        )
        return JSONResponse(
            content={"message": "Send mail request additional info success"},
            status_code=200,
            background=task,
        )


class PatientRegisterApi(HTTPEndpoint):
    async def post(self, form_data: RequestRegisterPatientSchema):
        """
        _summary_
        This function is used to register patient
        """
        try:
            avatar = None
            if isinstance(form_data.avatar, UploadFile):
                upload_file: UploadFile = form_data.avatar  # type: ignore
                s3_service = S3Service()
                await upload_file.seek(0)
                avatar = await s3_service.upload_file_from_form(upload_file)
            form_data.avatar = avatar
            patient_helper: PatientHelper = await Factory().get_patient_helper()
            result_respone = await patient_helper.create_patient(data=form_data)
            return result_respone
        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            raise InternalServer(
                msg="Internal server error", error_code=ErrorCode.SERVER_ERROR.name
            ) from e


class DoctorLocalRegisterApi(HTTPEndpoint):
    """
    This function is used to register doctor local
    """

    async def post(
        self, form_data: RequestRegisterDoctorLocalSchema, auth: JsonWebToken
    ):
        try:
            if auth.get("role", "") != Role.ADMIN.name:
                raise BadRequest(
                    msg="Unauthorized access",
                    error_code=ErrorCode.UNAUTHORIZED.name,
                    errors={"message": "You are not have permission to access"},
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
        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            raise InternalServer(
                msg="Internal server error",
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.name},
            ) from e


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
                        "message": "You are not authorized to access this resource"
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
        except (BadRequest, Forbidden) as e:
            raise e
        except Exception as e:
            log.error(f"Error: {e}")
            raise InternalServer(
                msg="Internal server error",
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": "Error when get all doctor not verify"},
            ) from e


class DoctorOtherRejectApiPut(HTTPEndpoint):
    async def put(self, path_params: RequestVerifyDoctorSchema, auth: JsonWebToken):
        try:
            if auth.get("role", "") != Role.ADMIN.name:
                raise Forbidden(
                    msg="Unauthorized access",
                    error_code=ErrorCode.UNAUTHORIZED.name,
                    errors={"message": "only admin can access"},
                )

            doctor_helper: DoctorHelper = await Factory().get_doctor_helper()
            result = await doctor_helper.verify_doctor(
                doctor_id=path_params.doctor_id, verify_status=-1, online_price=0
            )
            if result:
                return {"message": "Doctor verified successfully on status -1"}
            else:
                raise BadRequest(
                    msg="Doctor not found or already verified",
                    error_code=ErrorCode.NOT_FOUND.name,
                    errors={
                        "message": "Doctor not found or already verified on status -1"
                    },
                )
        except (Forbidden, BadRequest, NoResultFound) as e:
            raise e
        except Exception as e:
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": "Error when verify doctor"},
            ) from e


class DoctorOtherVerifyApiPut(HTTPEndpoint):
    async def put(self, path_params: RequestVerifyDoctorSchema, auth: JsonWebToken):
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
                return {"message": "Doctor verified successfully on status 1"}
            else:
                raise BadRequest(
                    msg="Doctor not found or already verified",
                    error_code=ErrorCode.NOT_FOUND.name,
                    errors={
                        "message": "Doctor not found or already verified on status 1"
                    },
                )
        except (Forbidden, BadRequest, NoResultFound) as e:
            raise e
        except Exception as e:
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": "Error when verify doctor"},
            ) from e


class DoctorForeignRegisterApi(HTTPEndpoint):
    async def post(self, form_data: RequestRegisterDoctorSchema):
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
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.name},
            )


class DoctorForeignRejectApi(HTTPEndpoint):

    async def put(self, path_params: RequestVerifyDoctorSchema, auth: JsonWebToken):
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
        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.name},
            ) from e


class LoginApi(HTTPEndpoint):
    async def post(self, form_data: RequestLoginSchema) -> Dict[str, Any]:
        user_helper: UserHelper = await Factory().get_user_helper()
        reponse_json = await user_helper.login(
            form_data.phone_number, form_data.password
        )
        return reponse_json


class LogoutApi(HTTPEndpoint):
    async def post(self, request: Request):
        header = request.headers.get("Authorization")
        if header:
            token = header.split(" ")[1]
            user_helper: UserHelper = await Factory().get_user_helper()
            reponse_json = await user_helper.logout(token)
            return reponse_json
        else:
            raise BadRequest(msg="Bad request", error_code=ErrorCode.BAD_REQUEST.name)


class DoctorOtherVerifyFinalApiPut(HTTPEndpoint):
    async def put(self, request: Request, auth: JsonWebToken):
        try:
            if auth.get("role", "") != Role.ADMIN.name:
                raise Forbidden(
                    msg="Unauthorized access",
                    error_code=ErrorCode.UNAUTHORIZED.name,
                    errors={"message": "only admin can access"},
                )
            form_data = await request.form()
            if not form_data:
                form_data = await request.json()

            if form_data.get("doctor_id") is None:
                raise BadRequest(
                    msg="Bad request",
                    error_code=ErrorCode.BAD_REQUEST.name,
                    errors={"message": "doctor_id is required"},
                )
            if form_data.get("online_price") is None:
                raise BadRequest(
                    msg="Bad request",
                    error_code=ErrorCode.BAD_REQUEST.name,
                    errors={"message": "online_price is required"},
                )

            doctor_helper: DoctorHelper = await Factory().get_doctor_helper()
            result = await doctor_helper.verify_doctor(
                doctor_id=form_data.get("doctor_id"),
                verify_status=2,
                online_price=form_data.get("online_price"),
            )
            if result:
                return {"message": "Doctor verified successfully on status 2"}
            else:
                raise BadRequest(
                    msg="Doctor not found or ",
                    error_code=ErrorCode.NOT_FOUND.name,
                    errors={
                        "message": "Doctor not found or already verified on status 2"
                    },
                )
        except (Forbidden, BadRequest, NoResultFound) as e:
            raise e
        except Exception as e:
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": "Error when verify doctor"},
            ) from e
