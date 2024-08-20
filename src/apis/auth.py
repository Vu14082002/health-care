from typing import Any, Dict, List, Union

import ujson

from src.core import HTTPEndpoint
from src.core.exception import BadRequest, InternalServer
from src.enum import ErrorCode
from src.factory import Factory
from src.helper.patient_helper import PatientHelper
from src.helper.user import UserHelper
from src.models.role import EnumRole, RoleModel
from src.models.user import UserModel
from src.schema.register import (RequestLoginSchema,
                                 RequestRegisterPatientSchema,
                                 ResponsePatientSchema)


class RegisterApi(HTTPEndpoint):
    async def post(self, form_data: RequestRegisterPatientSchema) -> Dict[str, Any]:
        try:
            patient_helper: PatientHelper = await Factory().get_patient_helper()
            response_data: ResponsePatientSchema = await patient_helper.create_patient(data=form_data)
            return response_data.model_dump()
        except BadRequest as e:
            raise e
        except InternalServer as e:
            raise e
        except Exception as e:
            raise InternalServer(msg="Internal server error",
                                 error_code=ErrorCode.SERVER_ERROR.name) from e


class DoctorRegisterApi(HTTPEndpoint):
    async def post(self, form_data: RequestRegisterPatientSchema) -> Dict[str, Any]:

        return {"message": "Doctor register success"}


class AdminRegisterApi(HTTPEndpoint):
    async def post(self, form_data: RequestRegisterPatientSchema) -> Dict[str, Any]:
        return {"message": "Admin register success"}


class LoginApi(HTTPEndpoint):
    async def post(self, form_data: RequestLoginSchema) -> Dict[str, Any]:

        user_helper: UserHelper = await Factory().get_user_helper()
        _ = await user_helper.login(form_data.phone, form_data.password)
        return {"message": "Login success"}
