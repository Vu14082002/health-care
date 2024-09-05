from datetime import date
from typing import Literal, Optional
from uuid import UUID

from click import File
from pydantic import BaseModel, ConfigDict, Field, field_serializer

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

    class Config:
        from_attributes = True


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


class RequestRegisterDoctorSchema(BaseModel):
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
    education: str | None = None
    account_number: str | None = None
    bank_name: str | None = None
    beneficiary_name: str | None = None
    branch_name: str | None = None
    password_hash: str = Field(alias="password")


class RequestVerifyDoctorSchema(BaseModel):
    doctor_id: int


class RequestRegisterDoctorOnlineSchema(RequestRegisterDoctorSchema):
    is_local_person: bool = Field(default=True)
    type_of_disease: Literal["online"] = Field(
        default=TypeOfDisease.ONLINE.value)
    verify_status: int = Field(default=2)
    online_price: float

    class Config:
        json_schema_extra = {
            "exclude": ["is_local_person", "type_of_disease", "verify_status"]
        }


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
