from math import e
from typing import TYPE_CHECKING

from sqlalchemy import Column, Date, ForeignKey, Integer, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.postgresql import Model

if TYPE_CHECKING:
    from src.models.doctor_model import DoctorModel
else:
    DoctorModel = "DoctorModel"


class WorkingScheduleModel(Model):
    __tablename__ = "working_schedule"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    doctor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('doctor.id'), nullable=False)

    work_date: Mapped[Date] = mapped_column(
        Date, nullable=False)

    start_time: Mapped[int] = mapped_column(
        Integer, nullable=False)

    end_time: Mapped[int] = mapped_column(
        Integer, nullable=False)

    doctor: Mapped["DoctorModel"] = relationship(
        "DoctorModel", back_populates="working_schedules")

    def __repr__(self):
        return f"<WorkingSchedule(id={self.id}, doctor_id={self.doctor_id}, work_date={self.work_date}, start_time={self.start_time}, end_time={self.end_time})>"

    def validate_time_slot(self):
        """Validate that the time slot is at least 3 hours."""
        delta = (self.end_time - self.start_time).total_seconds() / 3600
        if delta < 3:
            raise ValueError("Time slot must be at least 3 hours.")
