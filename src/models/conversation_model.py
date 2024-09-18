from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import JSON, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.postgresql import Model
from src.enum import PictureConversation

if TYPE_CHECKING:
    from src.models.message_model import MessageModel


class ConversationModel(Model):
    __tablename__ = "conversation"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    picture: Mapped[PictureConversation] = mapped_column(JSONB, nullable=False)
    # Relationships
    messages: Mapped[List["MessageModel"]] = relationship(
        "MessageModel", back_populates="conversation"
    )
