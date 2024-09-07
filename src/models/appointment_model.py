import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.postgresql import Model

if TYPE_CHECKING:
    from src.models.doctor_model import DoctorModel
    from src.models.patient_model import PatientModel
    from src.models.payment_model import PaymentModel


class AppointmentModelStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"


class AppointmentModelTypeStatus(enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"


class AppointmentModel(Model):
    __tablename__ = "appointment"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)

    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patient.id"), nullable=False)

    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("doctor.id"), nullable=False)

    appointment_date_start: Mapped[datetime] = mapped_column(
        DateTime, nullable=False)

    appointment_date_end: Mapped[datetime] = mapped_column(
        DateTime, nullable=False)

    appointment_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default=AppointmentModelStatus.APPROVED.value)

    examination_type: Mapped[str] = mapped_column(
        String(50), nullable=False)

    link_appointment: Mapped[str] = mapped_column(
        Text, nullable=True, default=None)

    patient: Mapped["PatientModel"] = relationship(
        "PatientModel", back_populates="appointments")

    doctor: Mapped["DoctorModel"] = relationship(
        "DoctorModel", back_populates="appointments")

    payment: Mapped["PaymentModel"] = relationship(
        "PaymentModel", back_populates="appointment")

    pre_examination_notes: Mapped[str] = mapped_column(Text, nullable=True)

    total_amount: Mapped[float] = mapped_column(
        Float, nullable=False)
