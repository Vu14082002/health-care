import enum
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.postgresql import Model

if TYPE_CHECKING:
    from . import (DoctorModel, MedicalRecordModel, PatientModel, PaymentModel,
                   WorkScheduleModel)


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

    work_schedule_id: Mapped[int] = mapped_column(
        ForeignKey("work_schedule.id"), nullable=False)

    appointment_status: Mapped[str] = mapped_column(
        String(50), nullable=False)

    link_appointment: Mapped[str] = mapped_column(
        Text, nullable=True, default=None)

    pre_examination_notes: Mapped[str |
                                  None] = mapped_column(Text, nullable=True)

    patient: Mapped["PatientModel"] = relationship(
        "PatientModel", back_populates="appointments", lazy="joined")

    doctor: Mapped["DoctorModel"] = relationship(
        "DoctorModel", back_populates="appointments", lazy="joined")

    payment: Mapped["PaymentModel"] = relationship(
        "PaymentModel", back_populates="appointment", lazy="joined")

    medical_record: Mapped["MedicalRecordModel"] = relationship(
        back_populates="appointment", uselist=False, lazy="joined")

    work_schedule: Mapped["WorkScheduleModel"] = relationship(
        "WorkScheduleModel", back_populates="appointment", lazy="joined")
