from datetime import date, datetime, time, timedelta
from typing import List, Optional, Tuple

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    validator,
)
from typing_extensions import Literal


class DoctorSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    id: int
    first_name: str
    last_name: str
    phone_number: str
    date_of_birth: str
    gender: str = Field(default="other")
    specialization: str
    certification: Optional[dict] = None
    hospital_address_work: Optional[str] = None
    address: str
    avatar: str
    description: Optional[str] = None


class RequestGetAllDoctorsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    key_word: str | None = None
    phone_number: str | None = None
    current_page: Optional[int] = Field(default=1)
    page_size: Optional[int] = Field(default=10)
    type_of_disease: Literal["online", "offline", "both"] | None = None
    is_local_person: bool | None = None


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
        from_attributes=True,
        use_enum_values=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True,
        extra="allow",
    )
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = None
    date_of_birth: str | None = None
    gender: Literal["male", "female", "other"] | None = None
    specialization: str | None = None
    certification: dict | None = None
    hopital_address_work: str | None = None
    address: str | None = None
    description: str | None = None
    password_hash: str | None = Field(alias="password", default=None)
    # avatar: UploadFile | None = None


class TimeSlot(BaseModel):
    start_time: time
    end_time: time

    @validator("start_time", "end_time", pre=True)
    def parse_time(cls, value):
        if isinstance(value, str):
            try:
                return time.fromisoformat(value.zfill(8))
            except ValueError:
                raise ValueError("Invalid time format. Use HH:MM:SS")
        return value

    @validator("end_time")
    def validate_time_slot(cls, v, values):
        start = values.get("start_time")
        if start and v:
            if v <= start:
                raise ValueError("End time must be after start time")
            if v < (datetime.combine(date.min, start) + timedelta(minutes=30)).time():
                raise ValueError("Time slot must be at least 30 minutes")
        return v


class DailySchedule(BaseModel):
    work_date: date
    time_slots: List[TimeSlot]


# FIXME eanble check past
# @validator('work_date')
# def validate_work_date(cls, v):
#     if v < date.today():
#         raise ValueError("Work date cannot be in the past")
#     return v


class RequestDoctorWorkScheduleNextWeek(BaseModel):
    doctor_id: Optional[int] = Field(
        default=None,
        description="If role login is ADMIN then doctor_id is required",
        examples=[1],
    )
    work_schedule: List[DailySchedule] = Field(
        ...,
        description="List of daily schedules for the next week",
        examples=["will be added"],
    )
    examination_type: Literal["online", "offline"] = Field(
        description="is type of examination, online or offline",
        examples=["online", "offline"],
    )

    # @validator('work_schedule')
    # def validate_work_schedule(cls, v):
    #     if len(v) == 0:
    #         raise ValueError("Work schedule cannot be empty")
    #     if len(v) > 7:
    #         raise ValueError("Work schedule cannot exceed 7 days")
    #     return v


class RequestGetWorkingTimeSchema(BaseModel):
    doctor_id: int | None = None
    start_date: date | None = None
    end_date: date | None = None
    examination_type: Literal["online", "offline"] | None = None
    ordered: bool | None = None

    class Config:
        json_encoders = {date: lambda v: v.isoformat()}

    @validator("doctor_id", pre=True)
    def refactor_doctor_id(cls, v):
        if v is None:
            return None
        return int(v)


class RequestGetWorkingTimeByIdSchema(BaseModel):
    id: int


class RequestGetWorkingTimeOrderedSchema(BaseModel):
    start_date: date | None = None
    end_date: date | None = None
    examination_type: Literal["online", "offline"] | None = None

    class Config:
        json_encoders = {date: lambda v: v.isoformat()}


class RequestGetUncenteredTimeSchema(BaseModel):
    doctor_id: int | None = None
    start_date: date
    end_date: date

    class Config:
        json_encoders = {date: lambda v: v.isoformat()}


class RequestGetWorkingSchedulesSchema(BaseModel):
    start_date: date
    end_date: date
    examination_type: Optional[Literal["online", "offline"]] = None

    class Config:
        json_encoders = {date: lambda v: v.isoformat()}


class RequestDoctorPatientSchema(BaseModel):
    doctor_id: Optional[int] = Field(
        default=None,
        description="This value is set only for role ADMIN. If value is None, then get all patients.",
        examples=["1"],
    )
    examination_type: Literal["online", "offline"] | None = Field(
        default=None,
        description="Type of examination. Default is online.",
        examples=["online", "offline", None],
    )
    current_page: Optional[int] = Field(
        default=1, description="Page number to get, starting from 1.", examples=["1"]
    )
    page_size: Optional[int] = Field(
        default=10, description="Number of items per page.", examples=["10"]
    )
    appointment_status: Optional[Literal["approved", "completed", "processing"]] = Field(
        default=None,
        description="If value is None, then get all appointments.",
        examples=["approved", "completed", "processing", " None"],
    )
    status_order: Optional[Tuple[str, ...]] = Field(
        default=("approved", "processing", "completed"),
        description="Order of statuses for sorting. If value is None, default order is used.",
        examples=["approved&processing&completed"],
    )
    text_search: str = Field(
        default=None,
        description="Search by patient name or phone number",
        examples=["John Handsome", "0123456789"],
    )

    @validator("status_order", pre=True, always=True)
    def parse_status_order(cls, value):
        if value is None:
            return ("approved", "processing", "completed")
        # Handle the case where value is a string of statuses separated by '&'
        if isinstance(value, str):
            return tuple(value.split("&"))
        return value


class RequestDoctorPatientByIdSchema(BaseModel):
    patient_id: int = Field(description="Patient id", examples=["1"])
