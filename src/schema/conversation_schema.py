from pydantic import BaseModel, Field


class RequestCreateConvertsationSchema(BaseModel):
    appointment_id: int = Field(
        description="is id of conversation",
        examples=[1],
    )


class RequestGetAllConversationSchema(BaseModel):
    text_search: str | None = Field(
        default=None, description="will select by phone for name "
    )
