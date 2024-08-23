from typing import Any, Dict, List, Union

import ujson

from src.core import HTTPEndpoint
from src.core.exception import BadRequest, InternalServer
from src.enum import ErrorCode
from src.factory import Factory
from src.helper.doctor_helper import DoctorHelper
from src.helper.patient_helper import PatientHelper
from src.helper.user_repository import UserHelper
from src.models.user import UserModel
from src.schema.register import (ReponseAdinSchema, ReponseDoctorSchema,
                                 RequestAdminRegisterSchema,
                                 RequestLoginSchema,
                                 RequestRegisterDoctorSchema,
                                 RequestRegisterPatientSchema,
                                 ResponsePatientSchema)


class PatientRegisterApi(HTTPEndpoint):
    async def post(self, form_data: RequestRegisterPatientSchema):
        try:
            patient_helper = await Factory().get_patient_helper()
            response_data = await patient_helper.create_patient(data=form_data)
            return response_data.model_dump()
        except BadRequest as e:
            raise e
        except InternalServer as e:
            raise e
        except Exception as e:
            raise InternalServer(msg="Internal server error",
                                 error_code=ErrorCode.SERVER_ERROR.name) from e


class DoctorPatientRegisterApi(HTTPEndpoint):
    async def post(self, form_data: RequestRegisterDoctorSchema):
        docker_helper = await Factory().get_doctor_helper()
        reulst = await docker_helper.create_doctor(form_data)
        reponse = ReponseDoctorSchema(**reulst.as_dict)
        return reponse.model_dump(mode="json")


class AdminRegisterApi(HTTPEndpoint):
    async def post(self, form_data: RequestAdminRegisterSchema):
        _user_helper: UserHelper = await Factory().get_user_helper()
        _result = await _user_helper.register_admin(form_data)
        _reponse = ReponseAdinSchema(**_result.as_dict)
        return _reponse.model_dump(mode="json")


class LoginApi(HTTPEndpoint):
    async def post(self, form_data: RequestLoginSchema) -> Dict[str, Any]:
        user_helper: UserHelper = await Factory().get_user_helper()
        reponse_json = await user_helper.login(form_data.phone_number, form_data.password)
        return reponse_json
