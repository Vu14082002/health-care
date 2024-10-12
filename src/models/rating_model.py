from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.postgresql import Model

if TYPE_CHECKING:
    from src.models.doctor_model import DoctorModel
    from src.models.patient_model import PatientModel


class RatingModel(Model):
    __tablename__ = "rating"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    doctor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("doctor.id"), nullable=False
    )

    patient_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("patient.id"), nullable=False
    )

    rating: Mapped[float] = mapped_column(Float, nullable=False)

    comment: Mapped[str] = mapped_column(Text, nullable=True)

    doctor: Mapped["DoctorModel"] = relationship(
        "DoctorModel", back_populates="ratings"
    )

    patient: Mapped["PatientModel"] = relationship(
        "PatientModel", back_populates="ratings"
    )

    def __repr__(self):
        return f"<Rating(id={self.id}, doctor_id={self.doctor_id}, patient_id={self.patient_id}, rating={self.rating})>"
