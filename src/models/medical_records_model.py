import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.apis import appointment
from src.core.database.postgresql import Model

if TYPE_CHECKING:
    from src.models.appointment_model import AppointmentModel
    from src.models.doctor_model import DoctorModel
    from src.models.patient_model import PatientModel
    from src.models.prescription_model import PrescriptionModel


class MedicalModelStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"


class MedicalRecordModel(Model):
    __tablename__ = "medical_record"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)

    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patient.id"), nullable=False)

    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("doctor.id"), nullable=False)

    appointment_id: Mapped[int] = mapped_column(
        ForeignKey("appointment.id"), nullable=False)

    diagnosis: Mapped[str] = mapped_column(Text, nullable=False)

    treatment_plan: Mapped[str] = mapped_column(Text, nullable=False)

    medications: Mapped[str] = mapped_column(Text, nullable=True)

    follow_up_instructions: Mapped[str] = mapped_column(Text, nullable=True)

    additional_notes: Mapped[str] = mapped_column(Text, nullable=True)

    # relation ship
    appointment: Mapped["AppointmentModel"] = relationship(
        "AppointmentModel", back_populates="medical_record")

    patient: Mapped["PatientModel"] = relationship(
        "PatientModel", back_populates="medical_records")

    doctor: Mapped["DoctorModel"] = relationship(
        "DoctorModel", back_populates="medical_records")
