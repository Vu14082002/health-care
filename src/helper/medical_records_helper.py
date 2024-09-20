import logging as log
from datetime import date, datetime, time, timedelta
from typing import Any, Dict, List, Literal, Optional

from sqlalchemy.exc import NoResultFound

from src.core.exception import BadRequest, InternalServer
from src.enum import ErrorCode
from src.repositories.medical_records_repository import MedicalRecordsRepository
from src.schema.medical_records_schema import RequestCreateMedicalRecordsSchema


class MedicalRecordsHelper:
    def __init__(self, *, medical_records_repository: MedicalRecordsRepository):
        self.medical_records_repository = medical_records_repository

    async def get_all_medical_records(
        self,
        current_page: int = 1,
        page_size: int = 10,
        join_: set[str] | None = None,
        where: dict[str, Any] = {},
        order_by: dict[str, str] = {"created_at": "desc"},
    ):
        try:
            skip = (current_page - 1) * page_size
            limit = page_size
            _medical_records = await self.medical_records_repository.get_all(
                skip, limit, join_, where, order_by
            )
            return _medical_records
        except Exception as e:
            log.error(e)
            raise e

    async def create_medical_records(self, *, value: dict[str, Any]):
        try:
            result = await self.medical_records_repository.create_medical_records(
                value=value
            )
            return result
        except (BadRequest, InternalServer) as e:
            raise e
        except Exception as e:
            log.error(e)
            raise InternalServer(
                msg="Internal server error",
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": "server is error, please try later"},
            ) from e

    async def update_medical_records(self, *, value: dict[str, Any]):
        try:
            result = await self.medical_records_repository.update_medical_records(
                value=value
            )
            return result
        except (BadRequest, InternalServer) as e:
            raise e
        except Exception as e:
            log.error(e)
            raise InternalServer(
                msg="Internal server error",
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": "server is error, please try later"},
            ) from e

    async def get_medical_records(self, user_id: int, role: str, doctor_id: int = None):
        try:
            records = await self.medical_records_repository.get_medical_records(
                user_id, role, doctor_id
            )
            return records
        except (BadRequest, InternalServer) as e:
            raise e
        except Exception as e:
            log.error(e)
            raise InternalServer(
                msg="Internal server error",
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": "server is error, please try later"},
            ) from e

    async def get_medical_record_by_appointment_id(
        self, user_id: int, appointment_id: int, role: str
    ):
        try:
            return await self.medical_records_repository.get_medical_record_by_appointment_id(
                user_id, appointment_id, role
            )
        except (BadRequest, InternalServer) as e:
            raise e
        except Exception as e:
            log.error(e)
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={
                    "message": "Error when get medical record by appointment id,pls try later"
                },
            )
