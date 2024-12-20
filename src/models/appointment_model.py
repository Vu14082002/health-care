import enum
import logging
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, Integer, Sequence, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.postgresql import Model

if TYPE_CHECKING:
    from . import (
        ConversationModel,
        DailyHealCheckModel,
        DoctorModel,
        MedicalRecordModel,
        PatientModel,
        PaymentModel,
        WorkScheduleModel,
    )

from sqlalchemy import event


class AppointmentModelStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    PROCESSING = "processing"


class AppointmentModelTypeStatus(enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"


class AppointmentModel(Model):
    __tablename__ = "appointment"
    __table_args__ = (
        Index("idx_appoint_name", "name"),
        Index("idx_appointment_status", "appointment_status"),
    )

    id: Mapped[int] = mapped_column(Integer, Sequence('appointment_id_seq', start=1000000, increment=1),primary_key=True, autoincrement=True,)

    name: Mapped[str] = mapped_column(String, nullable=True)

    patient_id: Mapped[int] = mapped_column(ForeignKey("patient.id"), nullable=False)

    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctor.id"), nullable=False)

    work_schedule_id: Mapped[int] = mapped_column(
        ForeignKey("work_schedule.id"), nullable=False
    )

    appointment_status: Mapped[str] = mapped_column(String(50), nullable=False)

    link_appointment: Mapped[str] = mapped_column(Text, nullable=True, default=None)

    pre_examination_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    patient: Mapped["PatientModel"] = relationship(
        "PatientModel", back_populates="appointments", lazy="joined"
    )

    doctor: Mapped["DoctorModel"] = relationship(
        "DoctorModel", back_populates="appointments", lazy="joined"
    )

    payment: Mapped["PaymentModel"] = relationship(
        "PaymentModel", back_populates="appointment", lazy="joined"
    )

    medical_record: Mapped["MedicalRecordModel"] = relationship(
        back_populates="appointment", uselist=False, lazy="joined"
    )

    work_schedule: Mapped["WorkScheduleModel"] = relationship(
        "WorkScheduleModel", back_populates="appointment", lazy="joined"
    )
    daily_health_checks: Mapped[list["DailyHealCheckModel"]] = relationship(
        "DailyHealCheckModel",
        back_populates="appointment",
    )
    conversation: Mapped["ConversationModel"] = relationship(
        "ConversationModel", back_populates="appointment", uselist=False
    )

    @staticmethod
    async def set_before_insert(mapper, connection, target):
        target.appointment_status = AppointmentModelStatus.PENDING.value
        if target.appointment_status not in [
            AppointmentModelStatus.PENDING.value,
            AppointmentModelStatus.APPROVED.value,
            AppointmentModelStatus.REJECTED.value,
            AppointmentModelStatus.COMPLETED.value,
        ]:
            logging.error("From set_before_insert appointment status is invalid")
            logging.error(
                "target.appointment_status must is in ['pending', 'approved', 'rejected', 'completed']"
            )
            raise ValueError("Invalid appointment status", target.appointment_status)


# Attach event listeners
event.listen(Model, "before_insert", AppointmentModel.set_before_insert)
