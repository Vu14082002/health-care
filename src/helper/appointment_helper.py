from src.core.decorator.exception_decorator import catch_error_helper
from src.repositories.appointment_repository import AppointmentRepository


class AppointmentHelper:
    def __init__(self, appointment_repository: AppointmentRepository):
        self.appointment_repository = appointment_repository

    @catch_error_helper(message=None)
    async def create_appointment(
        self,
        patient_id: int,
        name: str,
        doctor_id: int,
        work_schedule_id: int,
        pre_examination_notes: str | None = "",
    ):
        return await self.appointment_repository.create_appointment(
            patient_id, name, doctor_id, work_schedule_id, pre_examination_notes
        )

    @catch_error_helper(message=None)
    async def get_all_appointments(self, **kwargs):
        result = await self.appointment_repository.find(**kwargs)
        return result

    @catch_error_helper(message=None)
    async def statistical_appointment(self,year: int):
        return await self.appointment_repository.statistical_appointment(year=year)
