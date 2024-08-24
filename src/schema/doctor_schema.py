

from typing import Annotated, Optional

from pydantic import (BaseModel, ConfigDict, Field, field_validator,
                      model_validator)
from starlette.datastructures import UploadFile
from typing_extensions import Any, Literal


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
