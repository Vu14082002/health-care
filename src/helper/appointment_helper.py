import logging
from datetime import date
from typing import Literal, Optional

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
        cancel_url:str|None =None
    ):
        return await self.appointment_repository.create_appointment(
            patient_id,
            name,
            doctor_id,
            work_schedule_id,
            pre_examination_notes,
            is_payment=is_payment,
            call_back_url=call_back_url,
            cancel_url=cancel_url
        )
    @catch_error_helper(message=None)
    async def create_appointment_with_payment(self, payment_id: str, status_code:str):
        logging.info(f"create_appointment_with_payment with data : {payment_id} and status_code: {status_code}")
        _result = await self.appointment_repository.create_appointment_with_payment(
            payment_id=payment_id, status_code=status_code
        )
        logging.info(f"create_appointment_with_payment: {_result}")
        return _result

    @catch_error_helper(message=None)
    async def get_all_appointments(self, **kwargs):
        result = await self.appointment_repository.find(**kwargs)
        return result

    @catch_error_helper(message=None)
    async def statistical_appointment(self,year: int):
        return await self.appointment_repository.statistical_appointment(year=year)

    @catch_error_helper(message=None)
    async def statistical_appointment_with_work(self,user_id: int,from_date: date,to_date: date):
        # return await self.appointment_repository.statistical_appointment(year=year)
        return {"message": "Tinh nang dang duoc phat trien"}


    @catch_error_helper(message=None)
    async def statistical_appointment_sum_with_group_by_patient(
        self, doctor_id: int, examination_type: Literal["online", "offline"]
    ):
        return await self.appointment_repository.statistical_appointment_sum_with_group_by_patient(
            doctor_id, examination_type
        )
    @catch_error_helper(message=None)
    async def delete_appointment(self, appointment_id: int, patient_id: int):
        return await self.appointment_repository.delete_appointment(
            appointment_id, patient_id
        )
    @catch_error_helper(message=None)
    async def statistical_price(self, year:Optional[int]):
        return await self.appointment_repository.statistical_price(year=year)

    @catch_error_helper(message=None)
    async def statistical_price_all_doctor(self,from_date:date, to_date:date):
        return await self.appointment_repository.statistical_price_all_doctor( from_date, to_date)

    @catch_error_helper(message=None)
    async def statistical_price_all_patient(self,from_date:date, to_date:date):
        return await self.appointment_repository.statistical_price_all_patients( from_date, to_date)

    @catch_error_helper(message=None)
    async def statistical_price_person(self, from_date:date, to_date:date ,user_id:int):
        return await self.appointment_repository.statistical_price_person(from_date,to_date,user_id)


    @catch_error_helper(message=None)
    async def get_appointment_bill(self, appointment_id: int,user_id:int |None):
        return await self.appointment_repository.get_appointment_bill(appointment_id,user_id)
    @catch_error_helper(message=None)
    async def get_appointment_bills(
        self,
        from_date: date | None,
        to_date: date | None,
        doctor_name: str | None,
        doctor_phone: str | None,
        patient_name: str | None,
        patient_phone: str | None,
        user_id: int | None,
    ):
        _data = await self.appointment_repository.get_appointment_bills(
            from_date=from_date,
            to_date=to_date,
            doctor_name=doctor_name,
            doctor_phone=doctor_phone,
            patient_name=patient_name,
            patient_phone=patient_phone,
            user_id=user_id,
        )
        return _data
