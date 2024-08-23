

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DoctorsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    id: int
    first_name: str
    last_name: str
    date_of_birth: str
    gender: str
    phone_number: str
    address: str
    nation: str
    avatar: str


class ReponseGetAllDoctorsSchame(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    data: list[DoctorsSchema]
    current_page: int
    total_page: int
    page_size: int
