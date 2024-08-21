from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import UUID, Column, ForeignKey, Integer, String, Text, event
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.postgresql import Model

if TYPE_CHECKING:
    from src.models.doctor_model import DoctorModel
    from src.models.patient_model import PatientModel
else:
    DoctorModel = "DoctorModel"
    PatientModel = "PatientModel"


class DermatologyMedicalRecords(Model):
    __tablename__ = "dermatology_medical_records"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)

    patient_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('patient.id'), nullable=False
    )

    doctor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('doctor.id'), nullable=False
    )

    record_number: Mapped[str] = mapped_column(
        String(36), unique=True, nullable=False, default=lambda: str(uuid4())
    )

    diagnosis: Mapped[str] = mapped_column(Text, nullable=False)

    treatment_plan: Mapped[str] = mapped_column(Text, nullable=False)

    medications: Mapped[str] = mapped_column(Text, nullable=True)

    follow_up_instructions: Mapped[str] = mapped_column(Text, nullable=True)

    additional_notes: Mapped[str] = mapped_column(Text, nullable=True)

    patient: Mapped["PatientModel"] = relationship(
        "PatientModel", back_populates="dermatology_records"
    )

    doctor: Mapped["DoctorModel"] = relationship(
        "DoctorModel", back_populates="dermatology_records"
    )

    def __repr__(self):
        return f"<DermatologyMedicalRecords(id={self.id}, record_number='{self.record_number}', patient_id={self.patient_id}, doctor_id={self.doctor_id}, diagnosis='{self.diagnosis}')>"
