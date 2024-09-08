

from datetime import date, datetime, time
from typing import List, Literal

from pydantic import BaseModel, validator


class RequestRegisterAppointment(BaseModel):
    patient_id: int | None = None
    doctor_id: int
    work_schedule_id: int
    pre_examination_notes: str | None = None


class RequestGetAllAppointmentSchema(BaseModel):
    appointment_status: Literal["pending", "approved",
                                "rejected", "completed"] | None = None
    from_date: date | None = None
    to_date: date | None = None
    examination_type: Literal["online", "offline"] | None = None
    current_page: int | None = 1
    page_size: int | None = 10
    doctor_name: str | None = None
    patient_name: str | None = None

    class Config:
        json_encoders = {date: lambda v: v.isoformat()}

    # @validator('from_date', 'to_date', pre=True)
    # def parse_time(cls, value):
    #     if isinstance(value, str):
    #         try:
    #             return time.fromisoformat(value.zfill(8))
    #         except ValueError:
    #             raise ValueError("Invalid time format. Use HH:MM:SS")
    #     return value
