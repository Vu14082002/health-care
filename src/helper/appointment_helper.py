from typing import Any, Dict, List

from src.core.exception import BadRequest
from src.models.appointment_model import AppointmentModel
from src.repositories.appointment_repository import AppointmentRepository


class AppointmentHelper:
    def __init__(self, appointment_repository: AppointmentRepository):
        self.appointment_repository = appointment_repository

    async def create_appointment(
        self,
        patient_id: int,
        doctor_id: int,
        work_schedule_id: int,
        pre_examination_notes: str | None = "",
    ):
        try:
            return await self.appointment_repository.create_appointment(
                patient_id, doctor_id, work_schedule_id, pre_examination_notes
            )
        except BadRequest as e:
            raise e
        except Exception as e:
            raise e

    async def get_all_appointments(self, **kwargs):
        result = await self.appointment_repository.find(**kwargs)
        return result
