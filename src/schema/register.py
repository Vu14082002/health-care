from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_serializer


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
    password: str


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
    phone_number_urgent: str | None = None
    created_at: int = -1
    updated_at: int = -1
    is_deleted: bool = False

    # @field_serializer('id')
    # def serialize_dt(self, identifier: UUID, _info):
    #     return str(identifier)


class RequestLoginSchema(BaseModel):
    phone: str
    password: str
