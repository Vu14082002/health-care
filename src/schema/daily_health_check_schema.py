from typing import Any
from pydantic import BaseModel, Field

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


class DailyHealthCheckSchema(BaseModel):
    patient_id: int
    temperature: float
    assessment: str
    describe_health: str
    link_image_data: list[ImageDailyHealthCheck] | None
