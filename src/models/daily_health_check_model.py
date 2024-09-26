from sqlalchemy import Float, ForeignKey, Integer, String, Text, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from src.core.database.postgresql import Model
from typing import TYPE_CHECKING
from datetime import date
from src.enum import ImageDailyHealthCheck

if TYPE_CHECKING:
    from src.models.patient_model import PatientModel
    from src.models.appointment_model import AppointmentModel


class DailyHealCheckModel(Model):
    __tablename__ = "daily_health_check"
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
