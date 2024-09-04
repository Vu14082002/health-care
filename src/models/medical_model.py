import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.postgresql import Model

if TYPE_CHECKING:
    from src.models.doctor_model import DoctorModel
    from src.models.patient_model import PatientModel
else:
    DoctorModel = "DoctorModel"
    PatientModel = "PatientModel"


class MedicalModelStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"


class MedicalModel(Model):
    __tablename__ = "medical"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)

    # patient_id: Mapped[int] = mapped_column(
    #     ForeignKey("patient.id"), nullable=False)

    insurance_provider: Mapped[str | None] = mapped_column(
        String, nullable=True)

    current_medication: Mapped[str | None] = mapped_column(
        Text, nullable=True, default="")

    # doctor_id: Mapped[int] = mapped_column(
    #     ForeignKey("doctor.id"), nullable=False)

    appointment_date_start: Mapped[datetime] = mapped_column(
        DateTime, nullable=False)

    appointment_date_end: Mapped[datetime] = mapped_column(
        DateTime, nullable=False)

    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default=MedicalModelStatus.PENDING.value)

    # patient: Mapped["PatientModel"] = relationship(
    #     "PatientModel", back_populates="medicals")

    # doctor: Mapped["DoctorModel"] = relationship(
    #     "DoctorModel", back_populates="medicals")
