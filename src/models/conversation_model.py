from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import JSON, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.postgresql import Model

if TYPE_CHECKING:
    from src.models.message_model import MessageModel
    from src.models.user_model import UserModel


class ConversationModel(Model):
    __tablename__ = "conversation"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    messages: Mapped[List["MessageModel"]] = relationship(
        "MessageModel", back_populates="conversation"
    )
    users: Mapped[List["ConversationUserModel"]] = relationship(
        "ConversationUserModel", back_populates="conversation"
    )


class ConversationUserModel(Model):
    __tablename__ = "conversation_user"
    conversation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("conversation.id"), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), primary_key=True)
    conversation: Mapped[ConversationModel] = relationship(
        "ConversationModel", back_populates="users"
    )
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="conversations")
