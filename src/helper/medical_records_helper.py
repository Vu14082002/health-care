import logging as log
from typing import Any

from src.core.decorator.exception_decorator import catch_error_helper
from src.core.exception import BadRequest, InternalServer
from src.enum import ErrorCode
from src.repositories.medical_records_repository import MedicalRecordsRepository


class MedicalRecordsHelper:
    def __init__(self, *, medical_records_repository: MedicalRecordsRepository):
        self.medical_records_repository = medical_records_repository

    @catch_error_helper(message=None)
    async def get_all_medical_records(
        self,
        current_page: int = 1,
        page_size: int = 10,
        join_: set[str] | None = None,
        where: dict[str, Any] = {},
        order_by: dict[str, str] = {"created_at": "desc"},
    ):
        skip = (current_page - 1) * page_size
        limit = page_size
        _medical_records = await self.medical_records_repository.get_all(
            skip, limit, join_, where, order_by
        )
        return _medical_records

    @catch_error_helper(message=None)
    async def create_medical_records(self, *, value: dict[str, Any]):
        result = await self.medical_records_repository.create_medical_records(
            value=value
        )
        return result

    @catch_error_helper(message=None)
    async def update_medical_records(self, *, value: dict[str, Any]):
        result = await self.medical_records_repository.update_medical_records(
            value=value
        )
        return result

    @catch_error_helper(message=None)
    async def get_medical_records(self, user_id: int, role: str, doctor_id: int = None):
        records = await self.medical_records_repository.get_medical_records(
            user_id, role, doctor_id
        )
        return records

    @catch_error_helper(message=None)
    async def get_medical_record_by_appointment_id(
        self, user_id: int, appointment_id: int, role: str
    ):
        return (
            await self.medical_records_repository.get_medical_record_by_appointment_id(
                user_id, appointment_id, role
            )
        )
