from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database.postgresql import Model

if TYPE_CHECKING:
    from src.models.doctor_model import DoctorModel
    from src.models.patient_model import PatientModel


class PrescriptionModel(Model):
    __tablename__ = "prescription"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("doctor.id"), nullable=False)
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patient.id"), nullable=False)
    medication_name: Mapped[str] = mapped_column(String, nullable=False)
    dosage: Mapped[str] = mapped_column(String, nullable=False)
    frequency: Mapped[str] = mapped_column(String, nullable=False)
    duration: Mapped[str] = mapped_column(String, nullable=False)
    instructions: Mapped[str] = mapped_column(Text, nullable=True)
    prescribed_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow)

    doctor: Mapped["DoctorModel"] = relationship(
        "DoctorModel", back_populates="prescriptions")
    patient: Mapped["PatientModel"] = relationship(
        "PatientModel", back_populates="prescriptions")
