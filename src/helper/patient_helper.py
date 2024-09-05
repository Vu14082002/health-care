import logging

from src.core.exception import BadRequest, InternalServer
from src.enum import ErrorCode
from src.models.patient_model import PatientModel
from src.repositories.patient_repository import PatientRepository
from src.repositories.user import UserRepository
from src.schema.register import (RequestRegisterPatientSchema,
                                 ResponsePatientSchema)


class PatientHelper:
    def __init__(self, patient_repository: PatientRepository) -> None:
        self.patient_repository: PatientRepository = patient_repository

    async def create_patient(self, data: RequestRegisterPatientSchema):
        try:
            result = await self.patient_repository.insert_patient(data)
            # data_response = ResponsePatientSchema.model_validate(result)
            return result
        except BadRequest as e:
            raise e
        except InternalServer as e:
            raise e
        except Exception as e:
            logging.error(e)
            raise BadRequest(msg="Failed to create patient, please try again later",
                             error_code=ErrorCode.SERVER_ERROR.name) from e
