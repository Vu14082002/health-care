import logging as log
import math
import time
from typing import Any, Dict, List

from sqlalchemy.orm.exc import NoResultFound

from src.models.doctor_model import DoctorModel
from src.models.work_schedule_model import WorkScheduleModel
from src.repositories.doctor_repository import DoctorRepository
from src.schema.doctor_schema import (DoctorSchema, ReponseGetAllDoctorsSchema,
                                      RequestDoctorWorkScheduleNextWeek)
from src.schema.register import RequestRegisterDoctorSchema


class DoctorHelper:
    def __init__(self, *, doctor_repository: DoctorRepository):
        self.doctor_repository = doctor_repository

    async def get_all_doctor(self, current_page: int = 1, page_size: int = 10, join_: set[str] | None = None, where: dict[str, Any] | None = None, order_by: dict[str, str] | None = None):
        try:
            skip = (current_page - 1) * page_size
            limit = page_size
            _doctors = await self.doctor_repository.get_all(skip, limit, join_, where, order_by)

            count_record = await self.doctor_repository.count_record(where)

            total_page = math.ceil(count_record / limit)
            return {"data": _doctors, "total_page": total_page, "current_page": current_page, "page_size": page_size}
        except Exception as e:
            raise e

    async def get_doctor_by_id(self, doctor_id: int):
        try:
            doctor = await self.doctor_repository.get_doctor_with_ratings(doctor_id=doctor_id)
            return doctor
        except NoResultFound as e:
            log.error(f"Doctor with id {doctor_id} not found")
            log.debug(e)
            return None
        except Exception as e:
            raise e

    async def create_doctor(self, data: dict[str, Any], *args: Any, **kwargs: Any) -> Any:
        try:
            doctor = await self.doctor_repository.insert(data)
            return doctor
        except Exception as e:
            raise e

    async def update_doctor(self, doctor_id: int, data: dict[str, Any]):
        try:

            doctor_model = await self.doctor_repository.get_by("id", doctor_id, unique=True)
            data = {k: v for k, v in data.items() if v is not None}
            doctor = await self.doctor_repository.update(doctor_model, data)
            return doctor
        except NoResultFound as e:
            log.error(f"Doctor with id {doctor_id} not found")
            log.debug(e)
            return None
        except Exception as e:
            log.error(f"Error: {e}")
            raise e

    async def create_doctor_work_schedule(self, doctor_id: int, data: RequestDoctorWorkScheduleNextWeek):
        try:
            reponse = await self.doctor_repository.add_workingschedule(doctor_id, data)
            return reponse
        except Exception as e:
            await self.doctor_repository.session.rollback()
            raise e

    async def verify_doctor(self, doctor_id: int) -> bool:
        try:
            doctor = await self.doctor_repository.get_by("id", doctor_id, unique=True)
            if doctor and doctor.verify_status == 0:
                updated_doctor = await self.doctor_repository.update_one(doctor, {"verify_status": 1})
                return updated_doctor is not None
            return False
        except NoResultFound:
            return False
        except Exception as e:
            log.error(f"Error verifying doctor: {e}")
            raise
