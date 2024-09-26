from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.postgresql import Model
import uuid

if TYPE_CHECKING:
    from src.models.message_model import MessageModel
    from src.models.user_model import UserModel


def generate_uuid():
    return str(uuid.uuid4())


class ConversationModel(Model):
    __tablename__ = "conversation"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)

    messages: Mapped[List["MessageModel"]] = relationship(
        "MessageModel",
        back_populates="conversation",
        order_by="desc(MessageModel.created_at)",
    )
    users: Mapped[List["ConversationUserModel"]] = relationship(
        "ConversationUserModel", back_populates="conversation"
    )

    @property
    def latest_message(self) -> "MessageModel | None":
        return self.messages[0] if self.examination_prices else None


class ConversationUserModel(Model):
    __tablename__ = "conversation_user"
    conversation_id: Mapped[str] = mapped_column(
        String, ForeignKey("conversation.id"), primary_key=True
    )

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), primary_key=True)

    conversation: Mapped[ConversationModel] = relationship(
        "ConversationModel", back_populates="users"
    )
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="conversations")
