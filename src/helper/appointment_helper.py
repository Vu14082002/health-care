from src.models.appointment_model import AppointmentModel
from src.repositories.appointment_repository import AppointmentRepository


class AppointmentHelper:
    def __init__(self, appointment_repository: AppointmentRepository):
        self.appointment_repository = appointment_repository

    async def create_appointment(self, patient_id: int, doctor_id: int, work_schedule_id: int, pre_examination_notes: str):
        return await self.appointment_repository.create_appointment(patient_id, doctor_id, work_schedule_id, pre_examination_notes)
