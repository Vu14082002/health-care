from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.postgresql import Model
from src.enum import MessageContentSchema

if TYPE_CHECKING:
    from src.models.conversation_model import ConversationModel
    from src.models.user_model import UserModel


class MessageModel(Model):
    __tablename__ = "message"
    __table_args__ = (
        Index("idx_message_sender_conversation", "sender_id", "conversation_id"),
        Index("idx_message_conversation", "conversation_id"),
        Index("idx_message_reply", "reply_id"),
        Index("idx_message_sender", "sender_id"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    sender_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id"), nullable=False
    )

    conversation_id: Mapped[str] = mapped_column(
        String, ForeignKey("conversation.id"), nullable=False
    )

    reply_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("message.id"), nullable=True
    )
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)

    message: Mapped[MessageContentSchema] = mapped_column(JSONB, nullable=True)

    # Relationships
    conversation: Mapped["ConversationModel"] = relationship(
        "ConversationModel", back_populates="messages"
    )

    sender: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="messages", lazy="joined"
    )
