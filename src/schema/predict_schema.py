from typing import Any

from pydantic import BaseModel, Field


class PredictSchema(BaseModel):
    image:Any = Field(..., title="Image file for predict")
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        extra = "forbid"
