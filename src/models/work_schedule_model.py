from datetime import date, time
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Date,
    Float,
    ForeignKey,
    Integer,
    String,
    Time,
    event,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.postgresql import Model
from src.enum import TypeOfDisease

if TYPE_CHECKING:
    from . import AppointmentModel, DoctorModel


class WorkScheduleModel(Model):
    __tablename__ = "work_schedule"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    doctor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("doctor.id"), nullable=False
    )

    work_date: Mapped[date] = mapped_column(Date, nullable=False)

    start_time: Mapped[time] = mapped_column(Time, nullable=False)

    end_time: Mapped[time] = mapped_column(Time, nullable=False)

    examination_type: Mapped[str] = mapped_column(String, nullable=False)

    ordered: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    medical_examination_fee: Mapped[float] = mapped_column(Float)

    # relationship
    doctor: Mapped["DoctorModel"] = relationship(
        "DoctorModel", back_populates="working_schedules", lazy="joined"
    )

    appointment: Mapped["AppointmentModel"] = relationship(
        "AppointmentModel", back_populates="work_schedule", lazy="joined", uselist=False
    )

    @staticmethod
    def cal_medical_examination_fee(mapper, connection, target):
        data_doctor = target.doctor
        examination_prices_model = target.doctor.latest_examination_price
        if not examination_prices_model:
            return

        if target.examination_type == TypeOfDisease.ONLINE.value:
            base_price = examination_prices_model.online_price
        else:
            base_price = examination_prices_model.offline_price

        if target.start_time < time(8, 0) or target.start_time > time(17, 0):
            target.medical_examination_fee = base_price * 2
        else:
            target.medical_examination_fee = base_price


# Add the event listener
event.listen(
    WorkScheduleModel, "before_insert", WorkScheduleModel.cal_medical_examination_fee
)
