from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.postgresql import Model

if TYPE_CHECKING:
    from src.models.appointment_model import AppointmentModel
    from src.models.doctor_model import DoctorModel
    from src.models.medical_records_model import MedicalRecordModel
    from src.models.rating_model import RatingModel
    from src.models.user_model import UserModel
    from src.models.daily_health_check_model import DailyHealCheckModel
default_avatar = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSn5k7ItLSv5Rd7mdIOYQyPuvfr26Q5cdjk2AMGgw3wnBLmZ5LTOUsXh0jQ92RgRGx8G6g&usqp=CAU"


class PatientModel(Model):
    __tablename__ = "patient"
    __table_args__ = (
        Index("ix_patient_first_name_last_name", "first_name", "last_name"),
        Index("ix_patient_phone_number", "phone_number"),
        Index("idx_patient_email", "email"),
    )

    # id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), primary_key=True)

    doctor_manage_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("doctor.id"), nullable=True, default=None
    )

    first_name: Mapped[str] = mapped_column(String, nullable=False)

    last_name: Mapped[str] = mapped_column(String, nullable=False)

    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)

    gender: Mapped[str] = mapped_column(String, nullable=False, default="other")

    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    phone_number: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    address: Mapped[str] = mapped_column(String, nullable=False)

    avatar: Mapped[str] = mapped_column(Text, nullable=True, default=default_avatar)

    occupation: Mapped[str] = mapped_column(String, nullable=False)

    emergancy_contact_number: Mapped[str | None] = mapped_column(String, nullable=True)

    blood_type: Mapped[str] = mapped_column(String, nullable=True)

    allergies: Mapped[str] = mapped_column(Text, nullable=True)

    chronic_conditions: Mapped[str] = mapped_column(Text, nullable=True)

    height: Mapped[float] = mapped_column(Float, nullable=True)

    weight: Mapped[float] = mapped_column(Float, nullable=True)

    account_number: Mapped[str | None] = mapped_column(Text, nullable=True)

    bank_name: Mapped[str | None] = mapped_column(Text, nullable=True)

    beneficiary_name: Mapped[str | None] = mapped_column(Text, nullable=True)

    branch_name: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped["UserModel"] = relationship(
        "UserModel",
        uselist=False,
        back_populates="patient",
        foreign_keys=[id],
    )

    appointments: Mapped[list["AppointmentModel"]] = relationship(
        "AppointmentModel", back_populates="patient"
    )

    ratings: Mapped[list["RatingModel"]] = relationship(
        "RatingModel", back_populates="patient"
    )

    # one to many
    medical_records: Mapped[list["MedicalRecordModel"]] = relationship(
        back_populates="patient"
    )
    # one to many
    medical_records: Mapped[list["MedicalRecordModel"]] = relationship(
        "MedicalRecordModel", back_populates="patient"
    )

    daily_health_checks: Mapped[list["DailyHealCheckModel"]] = relationship(
        "DailyHealCheckModel", back_populates="patient"
    )

    doctor_manage: Mapped["DoctorModel"] = relationship(
        "DoctorModel", back_populates="patients", foreign_keys=[doctor_manage_id]
    )

    def __repr__(self):
        return f"<Patient(id={self.id}, first_name='{self.first_name}', last_name='{self.last_name}')>"
