from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_serializer


class RequestRegisterPatientSchema(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: str
    phone_number: str
    address: str
    nation: str
    occupation: str
    insurance_number: str | None = None
    phone_number_urgent: str | None = None
    gender: Literal["male", "female", "other"] | None = "other"
    password: str


class ResponsePatientSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
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

    @field_serializer('id')
    def serialize_dt(self, identifier: UUID, _info):
        return str(identifier)


class RequestLoginSchema(BaseModel):
    phone: str
    password: str
