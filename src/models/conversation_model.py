from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.postgresql import Model

if TYPE_CHECKING:
    from src.models.appointment_model import AppointmentModel
    from src.models.message_model import MessageModel


def _random_uuid():
    import uuid

    return str(uuid.uuid4())


class ConversationModel(Model):
    __tablename__ = "conversation"
    # appointment_id
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_random_uuid)

    appointment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("appointment.id"), nullable=False, unique=True
    )

    appointment: Mapped["AppointmentModel"] = relationship(
        "AppointmentModel", back_populates="conversation", uselist=False
    )
    messages: Mapped[List["MessageModel"]] = relationship(
        "MessageModel",
        back_populates="conversation",
        order_by="desc(MessageModel.created_at)",
    )

    @property
    def latest_message(self) -> "MessageModel | None":
        return self.messages[0] if len(self.messages) else None
