import logging

from src.core.decorator.exception_decorator import catch_error_helper
from src.core.exception import BadRequest, InternalServer
from src.enum import ErrorCode
from src.repositories.patient_repository import PatientRepository
from src.schema.register import RequestRegisterPatientSchema


class PatientHelper:
    def __init__(self, patient_repository: PatientRepository) -> None:
        self.patient_repository: PatientRepository = patient_repository

    @catch_error_helper
    async def create_patient(self, data: RequestRegisterPatientSchema):
        try:
            result = await self.patient_repository.insert_patient(data)
            return result.as_dict
        except BadRequest as e:
            raise e
        except InternalServer as e:
            raise e
        except Exception as e:
            logging.error(e)
            raise BadRequest(
                msg="Failed to create patient, please try again later",
                error_code=ErrorCode.SERVER_ERROR.name,
            ) from e

    async def get_all_patient(
        self, condition: dict | None = None, *, curent_page: int = 1, page_size: int = 1
    ):
        try:
            result = await self.patient_repository.get_all_patient(
                skip=(curent_page - 1) * page_size, limit=page_size
            )
            return result
        except BadRequest as e:
            raise e
        except InternalServer as e:
            raise e
        except Exception as e:
            logging.error(e)
            raise BadRequest(
                msg="Failed to get all patient, please try again later",
                error_code=ErrorCode.SERVER_ERROR.name,
            ) from e
