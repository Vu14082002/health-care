from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


class StatisticalConversation(BaseModel):
    from_date:date| None = Field(None, description="From date", examples=["2021-01-01"])
    from_date:date| None = Field(None, description="To date", examples=["2021-01-01"])
    doctor_id:int | None= Field(None, description="Doctor id", examples=["1"])
    examination_type:Literal["online","offline",None]=Field(None,description="Examination type",examples=["online","offline",None])


class StatisticalPrice(BaseModel):
    year:int = Field(None, description="Year", examples=["2021"])

class StatisticalPricePerson(BaseModel):
    from_date:date = Field(..., description="From date", examples=["2021-01-01"])
    to_date:date = Field(..., description="To date", examples=["2021-01-01"])
    user_id: int | None = Field(None, description="User id", examples=["1"])

class StatisticalPriceAllDoctor(BaseModel):
    from_date:date = Field(..., description="From date", examples=["2021-01-01"])
    to_date:date = Field(..., description="To date", examples=["2021-01-01"])
class StatisticalPriceAllPatient(BaseModel):
    from_date:date = Field(..., description="From date", examples=["2021-01-01"])
    to_date:date = Field(..., description="To date", examples=["2021-01-01"])
