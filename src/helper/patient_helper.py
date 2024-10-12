from src.core.decorator.exception_decorator import catch_error_helper
from src.repositories.patient_repository import PatientRepository
from src.schema.rating_schema import RequestCreateRatingSchema
from src.schema.register import RequestRegisterPatientSchema


class PatientHelper:
    def __init__(self, patient_repository: PatientRepository) -> None:
        self.patient_repository: PatientRepository = patient_repository

    @catch_error_helper("Failed to create patient, please try again later")
    async def create_patient(self, data: RequestRegisterPatientSchema):
        result = await self.patient_repository.insert_patient(data)
        return result.as_dict

    @catch_error_helper(message="Failed to get patient by id, please try again later")
    async def get_all_patient(
        self, condition: dict | None = None, *, curent_page: int = 1, page_size: int = 1
    ):
        result = await self.patient_repository.get_all_patient(
            skip=(curent_page - 1) * page_size, limit=page_size
        )
        return result

    @catch_error_helper("Failed to get patient by id, please try again later")
    async def create_rating_helper(
        self, user_id: int, data_model: RequestCreateRatingSchema
    ):
        result = await self.patient_repository.create_rating_repository(
            user_id, data_model
        )
        return result
