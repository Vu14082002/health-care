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
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: int
    username: str


class QueryResponseSchema(BaseModel):

    items: list[QueryResponseItemSchema]
    page_size: int = 10
    page: int = 1
