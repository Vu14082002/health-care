from pydantic import BaseModel, Field, field_validator


class RequestCreateRatingSchema(BaseModel):
    doctor_id: int = Field(..., description="is doctor id")
    rating: float = Field(..., description="is level rating from 1 to 5")
    comment: str = Field(None, description="is comment")

    class Config:
        extra = "forbid"

    @field_validator("rating")
    def check_rating(cls, v):
        if v < 1 or v > 5:
            raise ValueError("rating must be from 1 to 5")
        return v
