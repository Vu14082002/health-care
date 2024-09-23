import logging as log
from typing import Any, Dict

from sqlalchemy.exc import NoResultFound
from starlette.datastructures import UploadFile
from starlette.requests import Request

from src.core import HTTPEndpoint
from src.core.exception import BadRequest, Forbidden, InternalServer
from src.core.security.authentication import JsonWebToken
from src.enum import ErrorCode, Role, TypeOfDisease
from src.factory import Factory
from src.helper.doctor_helper import DoctorHelper
from src.helper.patient_helper import PatientHelper
from src.helper.s3_helper import S3Service
from src.helper.user_repository import UserHelper
from src.models.doctor_model import DoctorModel
from src.models.patient_model import PatientModel
from src.schema.register import (
    ReponseAdminSchema,
    RequestAdminRegisterSchema,
    RequestGetAllDoctorsNotVerifySchema,
    RequestLoginSchema,
    RequestRegisterDoctorForeignSchema,
    RequestRegisterDoctorLocalSchema,
    RequestRegisterPatientSchema,
    RequestVerifyDoctorSchema,
)


class PatientRegisterApi(HTTPEndpoint):
    async def post(self, form_data: RequestRegisterPatientSchema):
        try:
            avatar = None
            if isinstance(form_data.avatar, UploadFile):
                upload_file: UploadFile = form_data.avatar  # type: ignore
                s3_service = S3Service()
                await upload_file.seek(0)
                avatar = await s3_service.upload_file_from_form(upload_file)
            form_data.avatar = avatar
            patient_helper: PatientHelper = await Factory().get_patient_helper()
            response_data: PatientModel = await patient_helper.create_patient(
                data=form_data
            )
            return response_data.as_dict
        except BadRequest as e:
            raise e
        except InternalServer as e:
            raise e
        except Exception as e:
            raise InternalServer(
                msg="Internal server error", error_code=ErrorCode.SERVER_ERROR.name
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
                    errors={"message": "You are not authorized to access this resource"},
                )

            doctor_helper: DoctorHelper = await Factory().get_doctor_helper()
            current_page = query_params.current_page
            page_size = query_params.page_size
            where = {}
            if query_params.verify_status is None:
                where.update({"verify_status": {"$in": [0, 1]}})
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
            result = await doctor_helper.verify_doctor(path_params.doctor_id)
            if result:
                return {"message": "Doctor verified successfully"}
            else:
                raise BadRequest(
                    msg="Doctor not found or already verified",
                    error_code=ErrorCode.NOT_FOUND.name,
                    errors={"message": "Doctor not found or already verified"},
                )
        except (Forbidden, BadRequest, NoResultFound) as e:
            raise e
        except Exception as e:
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": "Error when verify doctor"},
            ) from e


class DoctorForeignRegisterApi(HTTPEndpoint):
    async def post(self, form_data: RequestRegisterDoctorForeignSchema):
        try:
            avatar = None
            if isinstance(form_data.avatar, UploadFile):
                upload_file: UploadFile = form_data.avatar  # type: ignore
                s3_service = S3Service()
                await upload_file.seek(0)
                avatar = await s3_service.upload_file_from_form(upload_file)
            form_data.avatar = avatar
            doctor_helper = await Factory().get_doctor_helper()
            data = form_data.model_dump()
            data["verify_status"] = 0
            data["is_local_person"] = False
            data["type_of_disease"] = TypeOfDisease.ONLINE.value
            result: DoctorModel = await doctor_helper.create_doctor(data)
            return result.as_dict  # type: ignore
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


class DoctorLocalRegisterApi(HTTPEndpoint):
    async def post(self, form_data: RequestRegisterDoctorLocalSchema, auth: JsonWebToken):
        try:
            if auth.get("role", "") != Role.ADMIN.name:
                raise BadRequest(
                    msg="Unauthorized access",
                    error_code=ErrorCode.UNAUTHORIZED.name,
                    errors={"message": "only admin can access"},
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
            result: DoctorModel = await doctor_helper.create_doctor(data)
            return result.as_dict  # type: ignore
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


class AdminRegisterApi(HTTPEndpoint):
    async def post(self, form_data: RequestAdminRegisterSchema):
        try:
            _user_helper: UserHelper = await Factory().get_user_helper()
            _result = await _user_helper.register_admin(form_data)
            _reponse = ReponseAdminSchema(**_result.as_dict)
            return _reponse.model_dump(mode="json")
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


class LoginApi(HTTPEndpoint):
    async def post(self, form_data: RequestLoginSchema) -> Dict[str, Any]:
        user_helper: UserHelper = await Factory().get_user_helper()
        reponse_json = await user_helper.login(form_data.phone_number, form_data.password)
        return reponse_json


class LogoutApi(HTTPEndpoint):
    async def post(self, request: Request):
        if request.headers.get("Authorization"):
            token = request.headers.get("Authorization").split(" ")[1]
            user_helper: UserHelper = await Factory().get_user_helper()
            reponse_json = await user_helper.logout(token)
            return reponse_json
        else:
            raise BadRequest(msg="Bad request", error_code=ErrorCode.BAD_REQUEST.name)
