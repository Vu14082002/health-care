import logging
import logging as log
import math
from datetime import date, datetime, time, timedelta
from typing import Any, Dict, List, Literal, Optional

from sqlalchemy.exc import NoResultFound

from src.core.exception import BadRequest
from src.enum import ErrorCode
from src.models.doctor_model import DoctorModel, TypeOfDisease
from src.models.work_schedule_model import WorkScheduleModel
from src.repositories.doctor_repository import DoctorRepository
from src.schema.doctor_schema import (
    DoctorSchema,
    ReponseGetAllDoctorsSchema,
    RequestDoctorWorkScheduleNextWeek,
)
from src.schema.register import RequestRegisterDoctorSchema


class DoctorHelper:
    def __init__(self, *, doctor_repository: DoctorRepository):
        self.doctor_repository = doctor_repository

    async def get_doctor_statistics(self) -> Dict[str, Any]:
        try:

            total_doctors = await self.doctor_repository.count_record(
                {"verify_status": {"$eq": 2}, "is_local_person": True}
            )
            total_doctor_online = await self.doctor_repository.count_record(
                {
                    "$or": [
                        {"type_of_disease": TypeOfDisease.ONLINE.value},
                        {"type_of_disease": TypeOfDisease.BOTH.value},
                    ],
                    "verify_status": {"$eq": 2},
                    "is_local_person": True,
                }
            )
            total_doctor_ofline = await self.doctor_repository.count_record(
                {
                    "$or": [
                        {"type_of_disease": TypeOfDisease.ONLINE.value},
                        {"type_of_disease": TypeOfDisease.BOTH.value},
                    ],
                    "verify_status": {"$eq": 2},
                    "is_local_person": True,
                }
            )
            total_doctor_both = await self.doctor_repository.count_record(
                {
                    "type_of_disease": TypeOfDisease.BOTH.value,
                    "verify_status": {"$eq": 2},
                    "is_local_person": True,
                }
            )
            return {
                "total_doctors": total_doctors,
                "total_doctor_online": total_doctor_online,
                "total_doctor_ofline": total_doctor_ofline,
                "total_doctor_both": total_doctor_both,
            }
        except Exception as e:
            logging.error(f"Error in get_doctor_statistics: {e}")
            raise

    async def get_all_doctor(
        self,
        current_page: int = 1,
        page_size: int = 10,
        join_: set[str] | None = None,
        where: dict[str, Any] | None = None,
        order_by: dict[str, str] | None = None,
    ):
        try:

            skip = (current_page - 1) * page_size
            limit = page_size

            _doctors = await self.doctor_repository.get_all(
                skip, limit, join_, where, order_by
            )

            count_record = await self.doctor_repository.count_record(where)

            total_page = math.ceil(count_record / limit)
            return {
                "data": _doctors,
                "total_page": total_page,
                "current_page": current_page,
                "page_size": page_size,
            }
        except BadRequest as e:
            logging.error(f"Error in get_all_doctor: {e}")
            raise e
        except Exception as e:
            raise e

    async def get_doctor_by_id(self, doctor_id: int):
        try:
            doctor = await self.doctor_repository.get_doctor_with_ratings(
                doctor_id=doctor_id
            )
            return doctor
        except NoResultFound as e:
            log.error(f"Doctor with id {doctor_id} not found")
            log.debug(e)
            return None
        except Exception as e:
            raise e

    async def create_doctor(
        self, data: dict[str, Any], *args: Any, **kwargs: Any
    ) -> Any:
        try:
            doctor = await self.doctor_repository.insert(data)
            return doctor
        except Exception as e:
            raise e

    async def update_doctor(self, doctor_id: int, data: dict[str, Any]):
        try:

            doctor_model = await self.doctor_repository.get_by(
                "id", doctor_id, unique=True
            )
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

    async def create_doctor_work_schedule(
        self, doctor_id: int, data: RequestDoctorWorkScheduleNextWeek
    ):
        try:
            response = await self.doctor_repository.add_workingschedule(doctor_id, data)
            return response
        except BadRequest as e:
            logging.error(f"Error in create_doctor_work_schedule: {e}")
            raise e
        except Exception as ex:
            logging.error(f"Error in create_doctor_work_schedule: {ex}")
            raise ex

    async def verify_doctor(self, doctor_id: int) -> bool:
        try:
            doctor = await self.doctor_repository.get_by("id", doctor_id, unique=True)
            if doctor and doctor.verify_status == 0:
                updated_doctor: DoctorModel = await self.doctor_repository.update_one(
                    doctor, {"verify_status": 1}
                )
                return isinstance(updated_doctor, DoctorModel)
            return False
        except NoResultFound as e:
            logging.error(f"Doctor with id {doctor_id} not found")
            logging.info(e)
            return False
        except Exception as e:
            log.error(f"Error verifying doctor: {e}")
            raise e

    async def get_working_schedules(
        self,
        doctor_id: int | None,
        start_date: date | None,
        end_date: date | None,
        examination_type: Literal["online", "offline"] | None,
        ordered: bool | None = None,
    ) -> List[Dict[str, Any]]:
        try:
            return await self.doctor_repository.get_working_schedules(
                doctor_id, start_date, end_date, examination_type, ordered=ordered
            )
        except Exception as e:
            logging.error(f"Error in get_working_schedules: {e}")
            raise

    async def get_working_schedules_by_id(self, *, id: int):
        try:
            return await self.doctor_repository.get_working_schedules_by_id(id=id)
        except BadRequest as e:
            raise e
        except Exception as e:
            logging.error(f"Error in get_working_schedules: {e}")
            raise

    async def get_empty_working_time(
        self, doctor_id: int, start_date: date, end_date: date
    ) -> Dict[str, List[Dict[str, str]]]:
        try:
            occupied_slots = await self.doctor_repository.get_working_schedules_v2(
                doctor_id, start_date, end_date
            )
            empty_slots = self._generate_empty_slots(
                start_date, end_date, occupied_slots
            )
            return empty_slots
        except Exception as e:
            logging.error(f"Error in get_empty_working_time: {e}")
            raise

    def _generate_empty_slots(
        self, start_date: date, end_date: date, occupied_slots: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, str]]]:
        empty_slots = {}
        current_date = start_date
        while current_date <= end_date:
            day_slots = []
            start_time = datetime.combine(current_date, time(0, 0))
            end_time = datetime.combine(current_date, time(23, 59))

            while start_time < end_time:
                slot_end = start_time + timedelta(minutes=30)
                if not self._is_slot_occupied(start_time, slot_end, occupied_slots):
                    day_slots.append(
                        {
                            "start_time": start_time.strftime("%H:%M"),
                            "end_time": slot_end.strftime("%H:%M"),
                        }
                    )
                start_time = slot_end

            if day_slots:
                empty_slots[current_date.isoformat()] = day_slots
            current_date += timedelta(days=1)

        return empty_slots

    def _is_slot_occupied(
        self,
        start_time: datetime,
        end_time: datetime,
        occupied_slots: List[Dict[str, Any]],
    ) -> bool:
        for slot in occupied_slots:
            if slot["work_date"] == start_time.date():
                occupied_start = datetime.combine(slot["work_date"], slot["start_time"])
                occupied_end = datetime.combine(slot["work_date"], slot["end_time"])
                if (occupied_start <= start_time < occupied_end) or (
                    occupied_start < end_time <= occupied_end
                ):
                    return True
        return False

    async def get_patient_by_doctor_id(
        self,
        doctor_id: int | None,
        current_page: int = 1,
        page_size: int = 10,
        appointment_status: str | None = None,
        status_order: tuple[str, ...] = ("approved", "processing", "completed"),
        examination_type: Literal["online", "offline"] | None = None,
    ):
        try:
            return await self.doctor_repository.get_patient_by_doctor_id(
                doctor_id=doctor_id,
                current_page=current_page,
                page_size=page_size,
                appointment_status=appointment_status,
                status_order=status_order,
                examination_type=examination_type,
            )
        except Exception as e:
            logging.error(f"Error in get_patient_by_doctor_id: {e}")
            raise
