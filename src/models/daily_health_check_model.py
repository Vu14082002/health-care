from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.postgresql import Model
from src.enum import ImageDailyHealthCheck

if TYPE_CHECKING:
    from src.models.appointment_model import AppointmentModel
    from src.models.patient_model import PatientModel


class DailyHealCheckModel(Model):
    __tablename__ = "daily_health_check"
    __table_args__ = (
        Index("idx_daily_health_check_patient", "patient_id"),
        Index("idx_daily_health_check_appointment", "appointment_id"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    patient_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("patient.id"), nullable=False
    )
    appointment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("appointment.id"), nullable=True
    )
    temperature: Mapped[float] = mapped_column(Float, nullable=True, default=0)
    assessment: Mapped[str] = mapped_column(String, nullable=False)
    describe_health: Mapped[str] = mapped_column(Text, nullable=True)
    link_image_data: Mapped[ImageDailyHealthCheck] = mapped_column(JSONB, nullable=True)
    date_create: Mapped[date] = mapped_column(Date, nullable=True, default=date.today())

    patient: Mapped["PatientModel"] = relationship(
        "PatientModel", back_populates="daily_health_checks", lazy="joined"
    )
    appointment: Mapped["AppointmentModel"] = relationship(
        "AppointmentModel", back_populates="daily_health_checks", lazy="joined"
    )
