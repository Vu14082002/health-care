
from pydantic import BaseModel


class QuestionSchema(BaseModel):
    query: str
