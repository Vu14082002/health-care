from src.core.decorator.exception_decorator import catch_error_helper
from src.repositories.patient_repository import PatientRepository
from src.schema.rating_schema import RequestCreateRatingSchema


class PatientHelper:
    def __init__(self, patient_repository: PatientRepository) -> None:
        self.patient_repository: PatientRepository = patient_repository

    @catch_error_helper(message=None)
    async def get_all_patient(
        self, condition: dict | None = None, *, curent_page: int = 1, page_size: int = 1
    ):
        result = await self.patient_repository.get_all_patient(
            skip=(curent_page - 1) * page_size, limit=page_size
        )
        return result

    @catch_error_helper(message=None)
    async def create_rating_helper(
        self, user_id: int, data_model: RequestCreateRatingSchema
    ):
        result = await self.patient_repository.create_rating_repository(
            user_id, data_model
        )
        return result

    @catch_error_helper(message=None)
    async def count_patient(self):
        result = await self.patient_repository.count_patient()
        return {"total_patient": result}

    @catch_error_helper(message=None)
    async def age_distribution_patient(self):
        result = await self.patient_repository.age_distribution_patient_repository()
        return result
