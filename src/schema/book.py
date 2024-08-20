from pydantic import BaseModel, ConfigDict

class BookItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    user_id: int

class InsertBook(BaseModel):
    name: str
    user_id: int

class QueryBook(BaseModel):
    name: str

class QueryResponseSchema(BaseModel):
    items: list[BookItem]
