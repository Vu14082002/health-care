from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class RequestRegisterAppointment(BaseModel):
    patient_id: int | None = None
    name: str = Field(..., description="name of appointment", examples=["Kham Thuong"])
    doctor_id: int
    work_schedule_id: int
    pre_examination_notes: str | None = None

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        extra = "forbid"


class RequestGetAllAppointmentSchema(BaseModel):
    appointment_status: Literal["pending", "approved", "completed"] | None = Field(
        default=None,
        description="query appointment by status,if not assign will ignore ",
        examples=["pending", "approved", "completed", "None"],
    )

    from_date: date | None = Field(
        default=None,
        description="query appointment by from date,if not assign will ignore : value format yyy-MM-dd",
        examples=["2021-01-01"],
    )
    to_date: date | None = Field(
        default=None,
        description="query appointment by to date,if not assign will ignore : value format yyy-MM-dd",
        examples=["2021-01-01", "None"],
    )
    examination_type: Literal["online", "offline"] | None = Field(
        default=None,
        description="query appointment by examination type,if not assign will ignore",
        examples=["online", "offline", "None"],
    )
    current_page: int | None = Field(
        default=1,
        description="current page, if not assign will default 1",
        examples=[1],
    )
    page_size: int | None = Field(
        default=10,
        description="page size, if not assign will default 10",
        examples=[10],
    )
    doctor_name: str | None = Field(
        default=None,
        description="query appointment by doctor name,if not assign will ignore, if you is role doctor must be assign this value",
        examples=["None", "Nguyen Van Hieu"],
    )
    patient_name: str | None = Field(
        default=None,
        description="query appointment by patient name,if not assign will ignore, if you is role patient must be assign this value",
        examples=["None", "Nguyen Van Hieu"],
    )

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
