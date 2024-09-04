from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.postgresql import Model

if TYPE_CHECKING:
    from src.models.patient_model import PatientModel


class MedicalHistoryModel(Model):
    __tablename__ = "medical_history"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patient.id"), nullable=False, unique=True)
    past_surgeries: Mapped[str] = mapped_column(Text, nullable=True)
    family_history: Mapped[str] = mapped_column(Text, nullable=True)
    lifestyle_factors: Mapped[str] = mapped_column(Text, nullable=True)
    immunizations: Mapped[str] = mapped_column(Text, nullable=True)

    patient: Mapped["PatientModel"] = relationship(
        "PatientModel", back_populates="medical_history")
