import enum
from datetime import date, datetime, time
from typing import TYPE_CHECKING, Any

from sqlalchemy import (Boolean, Date, DateTime, Float, ForeignKey, Integer,
                        String, Text, Time)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm.properties import MappedColumn
from sqlalchemy.sql import func

from src.core.database.postgresql import Model

default_avatar = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQS0iv-HzCTjY2RQ7JLiYe23Rw2Osp-n9PqUg&s"

if TYPE_CHECKING:
    from src.models.appointment_model import AppointmentModel
    from src.models.dermatology_medical import DermatologyMedicalRecords
    from src.models.examination_record_model import ExaminationRecordModel
    from src.models.medical_test_model import MedicalTestModel
    from src.models.prescription_model import PrescriptionModel
    from src.models.rating_model import RatingModel
    from src.models.user_model import UserModel
    from src.models.work_schedule_model import WorkScheduleModel

# FIXME: working date online or offline


class TypeOfDisease(enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    BOTH = "both"


class DoctorExaminationPriceModel(Model):
    __tablename__ = "doctor_examination_price"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    doctor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('doctor.id'), nullable=False)
    offline_price: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0)
    online_price: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0)
    ot_price_fee: Mapped[float] = mapped_column(
        Float, nullable=False, default=200)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True)

    doctor: Mapped["DoctorModel"] = relationship(
        "DoctorModel", back_populates="examination_prices")


class DoctorModel(Model):
    __tablename__ = "doctor"

    id: Mapped[int] = mapped_column(
        Integer, ForeignKey('user.id'), primary_key=True)

    first_name: Mapped[str] = mapped_column(String, nullable=False)

    last_name: Mapped[str] = mapped_column(String, nullable=False)

    phone_number: Mapped[str] = mapped_column(
        String, nullable=False, unique=True)

    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)

    gender: Mapped[str] = mapped_column(
        String, nullable=False, default="other")

    specialization: Mapped[str] = mapped_column(
        String, nullable=False, default="dermatology")

    certification: Mapped[str | None] = mapped_column(Text, nullable=True)

    verify_status: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0)

    is_local_person: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True)

    diploma: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=True)

    type_of_disease: Mapped[str] = mapped_column(
        String, nullable=False)  # type: ignore

    hopital_address_work: Mapped[str | None] = mapped_column(
        String, nullable=True)

    address: Mapped[str] = mapped_column(String, nullable=False)

    avatar: Mapped[str] = mapped_column(
        Text, nullable=True, default=default_avatar)

    description: Mapped[str] = mapped_column(Text, nullable=True)

    email: Mapped[str] = mapped_column(String, nullable=True, unique=True)

    appointments: Mapped[list["AppointmentModel"]] = relationship(
        "AppointmentModel", back_populates="doctor"
    )

    ratings: Mapped["RatingModel"] = relationship(
        "RatingModel", back_populates="doctor"
    )

    user: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="doctor")

    dermatology_records: Mapped["DermatologyMedicalRecords"] = relationship(
        "DermatologyMedicalRecords", back_populates="doctor"
    )

    examination_record: Mapped[list["ExaminationRecordModel"]] = relationship(
        back_populates="doctor")

    license_number: Mapped[str] = mapped_column(
        String, nullable=False, unique=True)

    education: Mapped[str] = mapped_column(Text, nullable=True)

    account_number: Mapped[str | None] = mapped_column(Text, nullable=True)

    bank_name: Mapped[str | None] = mapped_column(Text, nullable=True)

    beneficiary_name: Mapped[str | None] = mapped_column(Text, nullable=True)

    branch_name: Mapped[str | None] = mapped_column(Text, nullable=True)

    # relationship
    prescriptions: Mapped[list["PrescriptionModel"]] = relationship(
        "PrescriptionModel", back_populates="doctor")

    medical_tests: Mapped[list["MedicalTestModel"]] = relationship(
        "MedicalTestModel", back_populates="doctor")

    working_schedules: Mapped[list["WorkScheduleModel"]] = relationship(
        "WorkScheduleModel", back_populates="doctor"
    )

    examination_prices: Mapped[list["DoctorExaminationPriceModel"]] = relationship(
        "DoctorExaminationPriceModel", back_populates="doctor", order_by="desc(DoctorExaminationPriceModel.created_at)"
    )

    @property
    def latest_examination_price(self) -> "DoctorExaminationPriceModel | None":
        return self.examination_prices[0] if self.examination_prices else None
