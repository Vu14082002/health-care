import logging
import logging as log
import math
from datetime import date, datetime, time, timedelta
from typing import Any, Dict, List, Literal, Optional

from sqlalchemy.exc import NoResultFound

from src.core.exception import BadRequest
from src.enum import ErrorCode
from src.repositories.medical_records_repository import \
    MedicalRecordsRepository


class MedicalRecordsHelper:
    def __init__(self, *, medical_records_repository: MedicalRecordsRepository):
        self.medical_records_repository = medical_records_repository

    async def get_all_medical_records(self, current_page: int = 1, page_size: int = 10, join_: set[str] | None = None, where: dict[str, Any] | None = None, order_by: dict[str, str] | None = None):
        try:
            skip = (current_page - 1) * page_size
            limit = page_size
            _medical_records = await self.medical_records_repository.get_all(skip, limit, join_, where, order_by)

            count_record = await self.medical_records_repository.count_record(where)

            total_page = math.ceil(count_record / limit)
            return {"data": _medical_records, "total_page": total_page, "current_page": current_page, "page_size": page_size}
        except Exception as e:
            raise e

    async def get_medical_records_by_id(self, medical_records_id: int):
        pass
