from typing import Any

from pydantic import BaseModel, Field


class RequestCreateMessageSchema(BaseModel):
    conversation_id: int = Field(..., description="Conversation ID", examples=[1])
    reply_id: int | None = Field(
        None, description="is id message reply id", examples=[1]
    )
    media: Any | bytes | None = Field(
        default=None,
        description="is file iof call api or byte if socket",
    )
    image: Any | bytes | None = Field(
        default=None,
        description="is file iof call api or byte if socket",
    )
    content: str | None = Field(None, description="content message", examples=["Hello"])

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class RequestGetMessageSchema(BaseModel):
    conversation_id: int = Field(..., description="Conversation ID", examples=[1])

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
