from typing import Literal
from uuid import UUID

from click import File
from numpy import add
from pydantic import BaseModel, ConfigDict, Field, field_serializer

from src.models.user import Role


class RequestRegisterPatientSchema(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: str
    gender: Literal["male", "female", "other"] | None = "other"
    phone_number: str
    address: str
    nation: str
    occupation: str
    insurance_number: str | None = None
    emergancy_contact_number: str | None = None
    password_hash: str = Field(alias="password")

    class Config:
        from_attributes = True


class RequestRegisterDoctorSchema(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    date_of_birth: str
    gender: Literal["male", "female", "other"] | None = "other"
    specialization: str
    experience_years: int
    insurance_number: str | None = None
    certifications: str | None = None
    hopital_address_work: str | None = None
    address: str
    nation: str
    password_hash: str = Field(alias="password")

    class Config:
        from_attributes = True


class ResponsePatientSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    first_name: str
    last_name: str
    date_of_birth: str
    gender: str
    phone_number: str
    address: str
    nation: str
    avatar: str
    occupation: str
    insurance_number: str | None = None
    emergancy_contact_number: str | None = None
    created_at: int = -1
    updated_at: int = -1
    is_deleted: bool = False


class RequestLoginSchema(BaseModel):
    phone: str
    password: str
