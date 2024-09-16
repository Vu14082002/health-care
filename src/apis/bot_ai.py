import logging as log
from inspect import Signature
from typing import Any, Dict, List, Union
from urllib import response

import requests
from pydantic import Json
from sqlalchemy.exc import NoResultFound
from starlette.datastructures import UploadFile
from starlette.requests import Request

from src.config import config
from src.core import HTTPEndpoint
from src.core.exception import BadRequest, Forbidden, InternalServer
from src.core.security.authentication import JsonWebToken
from src.enum import ErrorCode, Role
from src.factory import Factory
from src.helper.doctor_helper import DoctorHelper
from src.helper.patient_helper import PatientHelper
from src.helper.s3_helper import S3Service
from src.helper.user_repository import UserHelper
from src.models.doctor_model import DoctorModel, TypeOfDisease
from src.models.patient_model import PatientModel
from src.models.user_model import UserModel
from src.schema.bot_service_schema import QuestionSchema
from src.schema.register import (ReponseAdminSchema,
                                 RequestAdminRegisterSchema,
                                 RequestGetAllDoctorsNotVerifySchema,
                                 RequestLoginSchema,
                                 RequestRegisterDoctorBothSchema,
                                 RequestRegisterDoctorForeignSchema,
                                 RequestRegisterDoctorLocalSchema,
                                 RequestRegisterDoctorOfflineSchema,
                                 RequestRegisterPatientSchema,
                                 RequestVerifyDoctorSchema)


class BotServiceApi(HTTPEndpoint):
    async def get(self, query_params: QuestionSchema):
        try:
            data = query_params.model_dump()
            response_data = requests.get(
                config.BOT_SERVICE_URL, params=query_params.model_dump())
            if response_data.status_code == 200:
                return response_data.json()
            raise BadRequest(error_code=ErrorCode.BAD_REQUEST.name,
                             errors={"message": "Bot service error"})
        except BadRequest as e:
            raise e
        except Exception as e:
            raise InternalServer(msg="Internal server error",
                                 error_code=ErrorCode.SERVER_ERROR.name) from e
