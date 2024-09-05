from datetime import date, datetime, time
from math import e
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, Enum, ForeignKey, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.postgresql import Model
from src.models.doctor_model import TypeOfDisease

if TYPE_CHECKING:
    from src.models.doctor_model import DoctorModel
else:
    DoctorModel = "DoctorModel"


class WorkScheduleModel(Model):
    __tablename__ = "work_schedule"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    doctor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('doctor.id'), nullable=False)

    work_date: Mapped[date] = mapped_column(
        Date, nullable=False)

    start_time: Mapped[time] = mapped_column(
        Time, nullable=False)

    end_time: Mapped[time] = mapped_column(
        Time, nullable=False)

    examination_type: Mapped[str] = mapped_column(
        String, nullable=False)

    ordered: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    doctor: Mapped["DoctorModel"] = relationship(
        "DoctorModel", back_populates="working_schedules")

    def __repr__(self):
        return f"<WorkingSchedule(id={self.id}, doctor_id={self.doctor_id}, work_date={self.work_date}, start_time={self.start_time}, end_time={self.end_time})>"

    def validate_time_slot(self):
        """Validate that the time slot is at least 3 hours."""
        start_datetime = datetime.combine(date.today(), self.start_time)
        end_datetime = datetime.combine(date.today(), self.end_time)
        delta = (end_datetime - start_datetime).total_seconds() / 3600
        if delta < 3:
            raise ValueError("Time slot must be at least 3 hours.")
