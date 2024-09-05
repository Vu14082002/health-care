from typing import Any, Dict, List, Union

import ujson
from pydantic import Json
from starlette.requests import Request

from src.core import HTTPEndpoint
from src.core.exception import BadRequest, InternalServer
from src.enum import ErrorCode
from src.factory import Factory
from src.helper.doctor_helper import DoctorHelper
from src.helper.patient_helper import PatientHelper
from src.helper.user_repository import UserHelper
from src.lib.authentication import JsonWebToken
from src.models.doctor_model import DoctorModel, TypeOfDisease
from src.models.patient_model import PatientModel
from src.models.user_model import UserModel
from src.schema.register import (ReponseAdminSchema,
                                 RequestAdminRegisterSchema,
                                 RequestLoginSchema,
                                 RequestRegisterDoctorBothSchema,
                                 RequestRegisterDoctorOfflineSchema,
                                 RequestRegisterDoctorOnlineSchema,
                                 RequestRegisterPatientSchema)


class PatientRegisterApi(HTTPEndpoint):
    async def post(self, form_data: RequestRegisterPatientSchema):
        try:
            patient_helper: PatientHelper = await Factory().get_patient_helper()
            response_data: PatientModel = await patient_helper.create_patient(data=form_data)
            return response_data.as_dict  # type: ignore
        except BadRequest as e:
            raise e
        except InternalServer as e:
            raise e
        except Exception as e:
            raise InternalServer(msg="Internal server error",
                                 error_code=ErrorCode.SERVER_ERROR.name) from e


class DoctorOnlineRegisterApi(HTTPEndpoint):
    async def post(self, form_data: RequestRegisterDoctorOnlineSchema):
        doctor_helper = await Factory().get_doctor_helper()
        result: DoctorModel = await doctor_helper.create_doctor(form_data.model_dump())
        return result.as_dict  # type: ignore


class DoctorOfflineRegisterApi(HTTPEndpoint):
    async def post(self, form_data: RequestRegisterDoctorOfflineSchema, auth: JsonWebToken):
        if auth.get("role", "") != "ADMIN":
            raise BadRequest(msg="Unauthorized access",
                             error_code=ErrorCode.UNAUTHORIZED.name)
        doctor_helper = await Factory().get_doctor_helper()
        result: DoctorModel = await doctor_helper.create_doctor(form_data.model_dump())
        return result.as_dict  # type: ignore


class DoctorBothRegisterApi(HTTPEndpoint):
    async def post(self, form_data: RequestRegisterDoctorBothSchema, auth: JsonWebToken):
        if auth.get("role", "") != "ADMIN":
            raise BadRequest(msg="Unauthorized access",
                             error_code=ErrorCode.UNAUTHORIZED.name)
        doctor_helper = await Factory().get_doctor_helper()
        result: DoctorModel = await doctor_helper.create_doctor(form_data.model_dump())
        return result.as_dict


class AdminRegisterApi(HTTPEndpoint):
    async def post(self, form_data: RequestAdminRegisterSchema):
        _user_helper: UserHelper = await Factory().get_user_helper()
        _result = await _user_helper.register_admin(form_data)
        _reponse = ReponseAdminSchema(**_result.as_dict)
        return _reponse.model_dump(mode="json")


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
            raise BadRequest(msg="Bad request",
                             error_code=ErrorCode.BAD_REQUEST.name)
