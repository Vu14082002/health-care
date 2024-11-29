from datetime import date
from typing import Optional

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
        is_payment: bool = False,
        call_back_url: str | None = None,
    ):
        return await self.appointment_repository.create_appointment(
            patient_id,
            name,
            doctor_id,
            work_schedule_id,
            pre_examination_notes,
            is_payment=is_payment,
            call_back_url=call_back_url,
        )
    @catch_error_helper(message=None)
    async def create_appointment_with_payment(self, payment_id: str, status_code:str):
        _result = await self.appointment_repository.create_appointment_with_payment(
            payment_id, status_code=status_code
        )
        return _result

    @catch_error_helper(message=None)
    async def get_all_appointments(self, **kwargs):
        result = await self.appointment_repository.find(**kwargs)
        return result

    @catch_error_helper(message=None)
    async def statistical_appointment(self,year: int):
        return await self.appointment_repository.statistical_appointment(year=year)

    @catch_error_helper(message=None)
    async def delete_appointment(self, appointment_id: int, patient_id: int):
        return await self.appointment_repository.delete_appointment(
            appointment_id, patient_id
        )
    @catch_error_helper(message=None)
    async def statistical_price(self, year:Optional[int]):
        return await self.appointment_repository.statistical_price(year=year)

    @catch_error_helper(message=None)
    async def statistical_price_person(self, from_date:date, to_date:date ,user_id:int):
        return await self.appointment_repository.statistical_price_person(from_date,to_date,user_id)
