import json
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pydantic import Json
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.postgresql import Model
from src.enum import FileMessageSchema, MessageContentSchema

if TYPE_CHECKING:
    from src.models.conversation_model import ConversationModel
    from src.models.user_model import UserModel


class MessageModel(Model):
    __tablename__ = "message"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    sender_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id"), nullable=False
    )

    conversation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("conversation.id"), nullable=False
    )

    reply_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("message.id"), nullable=True
    )

    message: Mapped[MessageContentSchema | None] = mapped_column(JSONB, nullable=True)

    files: Mapped[List[FileMessageSchema] | None] = mapped_column(JSONB, default=[])

    location: Mapped[Dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    sticker: Mapped[str | None] = mapped_column(String, nullable=True)

    notification: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Relationships
    conversation: Mapped["ConversationModel"] = relationship(
        "ConversationModel", back_populates="messages"
    )
