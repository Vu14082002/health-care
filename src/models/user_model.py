from enum import Enum as PyEnum
from typing import TYPE_CHECKING, List

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.postgresql import Model

if TYPE_CHECKING:
    from src.models.conversation_model import ConversationUserModel
    from src.models.doctor_model import DoctorModel
    from src.models.message_model import MessageModel
    from src.models.notification_model import NotificationModel
    from src.models.patient_model import PatientModel


class Role(PyEnum):
    ADMIN = "ADMIN"
    DOCTOR = "DOCTOR"
    PATIENT = "PATIENT"


class UserModel(Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    phone_number: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    password_hash: Mapped[str] = mapped_column(String, nullable=False)

    role: Mapped[str] = mapped_column(String, nullable=False, default=Role.PATIENT.value)

    doctor: Mapped["DoctorModel"] = relationship(
        "DoctorModel",
        uselist=False,
        back_populates="user",
        lazy="joined",
        foreign_keys="[DoctorModel.id]",
    )
    patient: Mapped["PatientModel"] = relationship(
        "PatientModel",
        uselist=False,
        back_populates="user",
        lazy="joined",
        foreign_keys="[PatientModel.id]",
    )
    notifications: Mapped[List["NotificationModel"]] = relationship(
        "NotificationModel", back_populates="user"
    )
    messages: Mapped[List["MessageModel"]] = relationship(
        "MessageModel", back_populates="sender"
    )

    def __repr__(self):
        return f"<User(id={self.id}, phone_number='{self.phone_number}', role='{self.role}')>"
