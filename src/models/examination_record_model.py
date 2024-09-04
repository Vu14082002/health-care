from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.postgresql import Model

if TYPE_CHECKING:
    from src.models.doctor_model import DoctorModel
    from src.models.patient_model import PatientModel


class ExaminationRecordModel(Model):
    __tablename__ = "examination_record"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("doctor.id"), nullable=False)

    doctor: Mapped["DoctorModel"] = relationship(
        "DoctorModel", back_populates="examination_record")

    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patient.id"), nullable=False)
    patient: Mapped["PatientModel"] = relationship(
        "PatientModel", back_populates="examination_record")

    examination_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False)

    diagnosis: Mapped[str] = mapped_column(Text, nullable=False)
    treatment_plan: Mapped[str] = mapped_column(Text, nullable=False)

    notes: Mapped[str] = mapped_column(Text, nullable=True)
