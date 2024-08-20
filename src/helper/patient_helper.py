import logging

from src.core.exception import BadRequest, InternalServer
from src.enum import ErrorCode
from src.models.patient import PatientModel
from src.repositories.patient import PatientRepository
from src.repositories.user import UserRepository
from src.schema.register import (RequestRegisterPatientSchema,
                                 ResponsePatientSchema)


class PatientHelper:
    def __init__(self, patient_repository: PatientRepository) -> None:
        self.patient_repository: PatientRepository = patient_repository

    async def create_patient(self, data: RequestRegisterPatientSchema) -> ResponsePatientSchema:
        try:
            result: PatientModel = await self.patient_repository.insert_patient(data)
            data_response: ResponsePatientSchema = ResponsePatientSchema(
                **result.as_dict)
            return data_response
        except BadRequest as e:
            raise e
        except InternalServer as e:
            raise e
        except Exception as e:
            logging.error(e)
            raise BadRequest(msg="Failed to create patient, please try again later",
                             error_code=ErrorCode.SERVER_ERROR.name) from e
