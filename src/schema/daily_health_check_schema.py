from datetime import date
from typing import Any
from pydantic import BaseModel, Field, validator

from src.enum import ImageDailyHealthCheck


class RequestCreateHealthCheckSchema(BaseModel):
    patient_id: int | None = Field(
        ..., description="Patient ID, if role Admin this value must assign", examples=[1]
    )
    temperature: float = Field(
        ..., description="Temperature of the patient", examples=[36.5]
    )
    assessment: str = Field(
        default="Normal",
        description="Assessment of the patient",
        examples=["Some assessment"],
    )
    describe_health: str = Field(
        default="",
        description="Describe the health of the patient",
        examples=["Some description"],
    )
    img_arr: Any | None = Field(default=None, description="array img ...")

    date_create: date | None = Field(
        default_factory=date.today,
        description="Date of the create health check",
        examples=["2021-01-01"],
    )

    class Config:
        json_encoders = {date: lambda v: v.isoformat()}


class DailyHealthCheckSchema(BaseModel):
    patient_id: int
    temperature: float
    assessment: str
    describe_health: str
    link_image_data: list[ImageDailyHealthCheck] | None
    date_create: date | None = Field(
        default_factory=date.today,
        description="Date of the create health check",
        examples=["2021-01-01"],
    )
    # FIXME: This validator is not working
    # @validator("time")
    # def validate_date_range(cls, values):
    #     if values < datetime.now():
    #         raise ValueError("Date must be in the past")


class RequestGetAllDailyHealthSchema(BaseModel):
    patient_id: int | None = Field(
        default=None,
        description="Patient ID, if role patient will get all, if role Admin or Doctor this value must assign",
        examples=[1],
    )
    start_date: date | None = Field(
        default=None,
        description="From start date -> all if end_date not assigned",
        examples=["2021-01-01", None],
    )
    end_date: date | None = Field(
        default=None,
        description="Oldest -> end date if start_date not assigned",
        examples=["2021-01-01", None],
    )
    current_page: int = Field(
        default=1, description="Page number to get, starting from 1", examples=[1]
    )
    page_size: int = Field(
        default=10, description="Number of items per page, default = 10", examples=[10]
    )

    class Config:
        json_encoders = {date: lambda v: v.isoformat()}

    @validator("end_date")
    def validate_date_range(cls, v, values):
        start_date = values.get("start_date")
        if start_date and v:
            if v < start_date:
                raise ValueError("End date must be after start date")
        return v
