from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_serializer


class InsertSchema(BaseModel):
    username: str
    password: str


class UpdateSchema(BaseModel):
    username: str
    password: str
    id: int


class QuerySchema(BaseModel):
    username: str


class QueryResponseItemSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str


class QueryResponseSchema(BaseModel):

    items: list[QueryResponseItemSchema]
    page_size: int = 10
    page: int = 1


class TokenSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    date_of_birth: str | None
    gender: str
    phone_number: str
    address: str | None
    nation: str
    avatar: str
    occupation: str
    insurance_number: str | None
    emergancy_contact_number: str | None
    role: str = ''

    class Config:
        populate_by_name = True
        from_attributes = True

    # @field_serializer('id')
    # def serialize_dt(self, id: UUID, _info):
    #     return str(id)
