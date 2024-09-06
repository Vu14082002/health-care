import logging
import logging as log
import math
import time
from datetime import date
from typing import Any, Dict, List, Literal, Optional

from sqlalchemy.exc import NoResultFound

from src.core.exception import BadRequest
from src.enum import ErrorCode
from src.models.doctor_model import DoctorModel, TypeOfDisease
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
            response = await self.doctor_repository.add_workingschedule(doctor_id, data)
            return response
        except BadRequest as e:
            raise e
        except Exception as ex:
            raise ex

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

    async def update_doctor_work_schedule(self, doctor_id: int, examination_type: TypeOfDisease, schedules: List[Dict[str, Any]]) -> Dict[str, Any]:
        try:
            # Get the doctor's current type_of_disease
            doctor = await self.doctor_repository.get_by("id", doctor_id, unique=True)
            if not doctor:
                raise BadRequest(msg="Doctor not found",
                                 error_code=ErrorCode.DOCTOR_NOT_FOUND.name, errors={"message": "Not found docto"})

            if doctor.type_of_disease == TypeOfDisease.ONLINE.value and examination_type == TypeOfDisease.OFFLINE:
                raise BadRequest(msg="Doctor is only available for online examinations",
                                 error_code=ErrorCode.INVALID_EXAMINATION_TYPE.name)
            elif doctor.type_of_disease == TypeOfDisease.OFFLINE.value and examination_type == TypeOfDisease.ONLINE:
                raise BadRequest(msg="Doctor is only available for offline examinations",
                                 error_code=ErrorCode.INVALID_EXAMINATION_TYPE.name)

            # Get available slots for the other examination type
            other_type = TypeOfDisease.OFFLINE if examination_type == TypeOfDisease.ONLINE else TypeOfDisease.ONLINE
            start_date = min(schedule['work_date'] for schedule in schedules)
            end_date = max(schedule['work_date'] for schedule in schedules)
            available_slots = await self.doctor_repository.get_available_slots(doctor_id, other_type, start_date, end_date)

            # Update the work schedule
            result = await self.doctor_repository.update_work_schedule(doctor_id, examination_type, schedules)

            return {
                "message": result["message"],
                "available_slots": available_slots
            }
        except BadRequest as e:
            raise e
        except Exception as e:
            logging.error(f"Error in update_doctor_work_schedule: {e}")
            raise BadRequest(msg="Failed to update work schedule",
                             error_code=ErrorCode.SERVER_ERROR.name)

    async def get_uncentered_time(self, doctor_id: int, start_date: date, end_date: date):
        try:
            return await self.doctor_repository.get_uncentered_time(doctor_id, start_date, end_date)
        except Exception as e:
            logging.error(f"Error in get_uncentered_time: {e}")
            raise

    async def get_working_schedules(self, doctor_id: int | None, start_date: date | None, end_date: date | None, examination_type: Literal["online", "offline"] | None):
        try:
            return await self.doctor_repository.get_working_schedules(doctor_id, start_date, end_date, examination_type)
        except Exception as e:
            logging.error(f"Error in get_working_schedules: {e}")
            raise
