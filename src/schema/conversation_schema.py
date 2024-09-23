from pydantic import BaseModel, Field


class RequestCreateConvertsationSchema(BaseModel):
    participant_id: int = Field(
        description="is id of user who you want to create conversation with",
        examples=[1],
    )
