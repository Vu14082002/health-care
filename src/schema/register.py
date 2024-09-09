import json
import re
from datetime import date
from typing import Any, Literal, Optional
from uuid import UUID

from click import File
from pydantic import BaseModel, ConfigDict, Field, field_serializer, validator
from starlette.datastructures import UploadFile

from src.enum import TypeOfDisease
from src.lib.postgres import Base
from src.models.doctor_model import TypeOfDisease
from src.models.user_model import Role


class RequestRegisterPatientSchema(BaseModel):
    first_name: str
    last_name: str
    email: str
    date_of_birth: date
    gender: Literal["male", "female", "other"] | None = "other"
    phone_number: str
    address: str
    occupation: str
    emergancy_contact_number: str | None = None
    password_hash: str = Field(alias="password")
    account_number: str | None = None
    bank_name: str | None = None
    beneficiary_name: str | None = None
    branch_name: str | None = None
    avatar: Any | None = None

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class ResponsePatientSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str
    email: str
    phone_number: str
    address: str
    avatar: str
    occupation: str
    emergancy_contact_number: str | None = None
    blood_type: str | None = None
    allergies: str | None = None
    chronic_conditions: str | None = None


class Diploma(BaseModel):
    data: list[str] | None = None


class Education(BaseModel):
    data: list[str] | None = None


class RequestRegisterDoctorSchema(BaseModel):
    # model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    first_name: str
    last_name: str
    phone_number: str
    date_of_birth: date
    gender: Literal["male", "female", "other"] | None = "other"
    specialization: str
    certification: str | None = None
    diploma: Diploma | None = None
    hopital_address_work: str | None = None
    address: str
    description: str | None = None
    email: str | None = None
    license_number: str
    education: Education | None = None
    account_number: str | None = None
    bank_name: str | None = None
    beneficiary_name: str | None = None
    branch_name: str | None = None
    avatar: Any | None = None
    password_hash: str = Field(alias="password")

    @validator("education", pre=True)
    def check_education(cls, v):
        if isinstance(v, str):
            json_data = json.loads(v)
            if json_data.get("data"):
                data = Education(data=json_data.get("data"))
                return data
            raise ValueError(f"Invalid education data")

    @validator("diploma", pre=True)
    def check_diploma(cls, v):
        if isinstance(v, str):
            json_data = json.loads(v)
            if json_data.get("data"):
                data = Diploma(data=json_data.get("data"))
                return data
            raise ValueError(f"Invalid diploma data")


class RequestRegisterDoctorForeignSchema(RequestRegisterDoctorSchema):
    verify_status: int = Field(default=0, exclude=True)
    online_price: float
    is_local_person: bool = Field(default=True, examples=True)
    type_of_disease: Literal["online"] = Field(
        default=TypeOfDisease.ONLINE.value)

    @validator("is_local_person", pre=True)
    def convert_islocal(cls, v):
        return False

    @validator("type_of_disease", pre=True)
    def convert_type_of_disease(cls, v):
        return TypeOfDisease.ONLINE.value

    @validator("verify_status", pre=True)
    def convert_verify_status(cls, v):
        return 0


class RequestRegisterDoctorLocalSchema(RequestRegisterDoctorSchema):
    offline_price: Optional[float] = None
    online_price: Optional[float] = None
    is_local_person: bool = Field(default=True)
    type_of_disease: Literal[TypeOfDisease.BOTH.value,
                             TypeOfDisease.OFFLINE.value, TypeOfDisease.ONLINE.value]
    verify_status: int = Field(default=2, exclude=True)

    @validator("is_local_person", pre=True)
    def convert_islocal(cls, v):
        return True

    @validator("verify_status", pre=True)
    def convert_verify_status(cls, v):
        return 2

    @validator("type_of_disease")
    def check_type_of_disease(cls, v, values):
        offline_price = values.get("offline_price")
        online_price = values.get("online_price")

        if v not in [TypeOfDisease.BOTH.value, TypeOfDisease.OFFLINE.value, TypeOfDisease.ONLINE.value]:
            raise ValueError(f"Invalid type of disease")

        if v == TypeOfDisease.OFFLINE.value:
            if offline_price is None or offline_price <= 0:
                raise ValueError(f"Missing or invalid offline price")
            if online_price is not None:
                raise ValueError(
                    f"Online price should not be set for offline-only type")

        if v == TypeOfDisease.BOTH.value:
            if offline_price is None or offline_price <= 0 or online_price is None or online_price <= 0:
                raise ValueError(
                    f"Missing or invalid offline/online price for both types")

        if v == TypeOfDisease.ONLINE.value:
            if online_price is None or online_price <= 0:
                raise ValueError(f"Missing or invalid online price")
        return v


class RequestVerifyDoctorSchema(BaseModel):
    doctor_id: int


class RequestGetAllDoctorsNotVerifySchema(BaseModel):
    key_word: str | None = None
    phone_number: str | None = None
    current_page: Optional[int] = Field(default=1)
    page_size: Optional[int] = Field(default=10)

    class Config:
        json_schema_extra = {
            "exclude": ["is_local_person", "type_of_disease", "verify_status"]
        }
        from_attributes = True
        use_enum_values = True


class RequestRegisterDoctorOfflineSchema(RequestRegisterDoctorSchema):
    is_local_person: bool = Field(default=True)
    type_of_disease: Literal["offline"] = Field(
        default=TypeOfDisease.OFFLINE.value)
    verify_status: int = Field(default=2)
    offline_price: float

    class Config:
        json_schema_extra = {
            "exclude": ["is_local_person", "type_of_disease", "verify_status"]
        }


class RequestRegisterDoctorBothSchema(RequestRegisterDoctorSchema):
    is_local_person: bool = Field(default=True)
    type_of_disease: Literal["both"] = Field(
        default=TypeOfDisease.BOTH.value)
    verify_status: int = Field(default=2)
    offline_price: float
    online_price: float

    class Config:
        json_schema_extra = {
            "exclude": ["is_local_person", "type_of_disease", "verify_status"]
        }


class ReponseDoctorSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    id: int
    first_name: str
    last_name: str
    phone_number: str
    date_of_birth: date
    gender: Literal["male", "female", "other"]
    specialization: str
    certification: str | None = None
    hospital_address_work: Optional[str] = None
    address: str
    avatar: str
    description: Optional[str] = None
    license_number: str
    education: Optional[str] = None


class RequestAdminRegisterSchema(BaseModel):
    phone_number: str
    password_hash: str = Field(alias="password")


class ReponseAdminSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    phone_number: str
    created_at: int = -1
    updated_at: int = -1
    is_deleted: bool = False


class RequestLoginSchema(BaseModel):
    phone_number: str
    password: str
