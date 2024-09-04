from typing import Annotated, Optional

from pydantic import (BaseModel, ConfigDict, Field, field_validator,
                      model_validator)
from starlette.datastructures import UploadFile
from typing_extensions import Any, Literal
from datetime import date, time

class DoctorSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    id: int
    first_name: str
    last_name: str
    phone_number: str
    date_of_birth: str
    gender: str = Field(default="other")
    specialization: str
    experience_years: int
    insurance_number: Optional[str] = None
    certifications: Optional[str] = None
    hospital_address_work: Optional[str] = None
    address: str
    avatar: str
    description: Optional[str] = None
    nation: str


class RequestGetAllDoctorsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    key_word: str | None = None
    phone_number: str | None = None
    current_page: Optional[int] = Field(default=1)
    page_size: Optional[int] = Field(default=10)


class ReponseGetAllDoctorsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    items: list[DoctorSchema]
    current_page: int
    page_size: int
    total_page: int


class RequestDetailDoctorSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    doctor_id: int


class RequestUpdatePathParamsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    doctor_id: int


class RequestUpdateDoctorSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, use_enum_values=True, arbitrary_types_allowed=True, str_strip_whitespace=True, extra="allow")
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = None
    date_of_birth: str | None = None
    gender: Literal["male", "female", "other"] | None = None
    specialization: str | None = None
    experience_years: int | None = None
    insurance_number: str | None = None
    certifications: str | None = None
    hopital_address_work: str | None = None
    address: str | None = None
    nation: str | None = None
    description: str | None = None
    password_hash: str | None = Field(alias="password", default=None)
    # avatar: UploadFile | None = None


class RequestDockerWorkDateInNextWeek(BaseModel):
    pass


class DoctorWorkTimeSlot(BaseModel):
    work_date: date
    start_time: time
    end_time: time

    @field_validator('work_date')
    def validate_work_date(cls, v):
        if v < date.today():
            raise ValueError("Work date cannot be in the past")
        return v

    @model_validator(mode='after')
    def validate_time_slot(self):
        if (datetime.combine(date.today(), self.end_time) - 
            datetime.combine(date.today(), self.start_time)).total_seconds() / 3600 < 3:
            raise ValueError("Time slot must be at least 3 hours")
        return self

class RequestDoctorWorkScheduleNextWeek(BaseModel):
    doctor_id: int
    work_schedule: list[DoctorWorkTimeSlot]

    @field_validator('work_schedule')
    def validate_work_schedule(cls, v):
        if len(v) == 0:
            raise ValueError("Work schedule cannot be empty")
        if len(v) > 7:
            raise ValueError("Work schedule cannot exceed 7 days")
        return v
