from typing import Literal, Optional
from uuid import UUID

from click import File
from pydantic import BaseModel, ConfigDict, Field, field_serializer

from src.models.user_model import Role


class RequestRegisterPatientSchema(BaseModel):
    first_name: str
    last_name: str
    email: str
    date_of_birth: str
    gender: Literal["male", "female", "other"] | None = "other"
    phone_number: str
    address: str
    occupation: str
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
    certifications: dict | None = None
    hopital_address_work: str | None = None
    address: str
    license_number: str
    password_hash: str = Field(alias="password")
    email: str | None = None

    class Config:
        from_attributes = True


class RequestAdminRegisterSchema(BaseModel):
    phone_number: str
    password_hash: str = Field(alias="password")


class ReponseDoctorSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: int
    first_name: str
    last_name: str
    phone_number: str
    date_of_birth: str
    gender: Literal["male", "female", "other"]
    specialization: str
    experience_years: int
    certifications: Optional[dict] = None
    hospital_address_work: Optional[str] = None
    address: str
    avatar: str
    description: Optional[str] = None
    license_number: str
    education: Optional[str] = None


class ResponsePatientSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    first_name: str
    last_name: str
    date_of_birth: str
    gender: str
    phone_number: str
    address: str
    avatar: str
    occupation: str
    emergancy_contact_number: str | None = None
    created_at: int = -1
    updated_at: int = -1
    is_deleted: bool = False


class ReponseAdinSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    phone_number: str
    created_at: int = -1
    updated_at: int = -1
    is_deleted: bool = False


class RequestLoginSchema(BaseModel):
    phone_number: str
    password: str
