from datetime import date
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import (UUID, Column, Date, Float, ForeignKey, Integer, String,
                        Text, event)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.postgresql import Model
from src.models import medical_records_model
from src.models.medical_records_model import MedicalRecordModel

if TYPE_CHECKING:
    from src.models.appointment_model import AppointmentModel
    from src.models.rating_model import RatingModel
    from src.models.user_model import UserModel

default_avatar = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSn5k7ItLSv5Rd7mdIOYQyPuvfr26Q5cdjk2AMGgw3wnBLmZ5LTOUsXh0jQ92RgRGx8G6g&usqp=CAU"


class PatientModel(Model):
    __tablename__ = "patient"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    first_name: Mapped[str] = mapped_column(String, nullable=False)

    last_name: Mapped[str] = mapped_column(String, nullable=False)

    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)

    gender: Mapped[str] = mapped_column(
        String, nullable=False, default="other")

    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    phone_number: Mapped[str] = mapped_column(
        String, nullable=False, unique=True)

    address: Mapped[str] = mapped_column(String, nullable=False)

    avatar: Mapped[str] = mapped_column(
        Text, nullable=True, default=default_avatar)

    occupation: Mapped[str] = mapped_column(String, nullable=False)

    emergancy_contact_number: Mapped[str | None] = mapped_column(
        String, nullable=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

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
        "UserModel", uselist=False, back_populates="patient")

    appointments: Mapped[list["AppointmentModel"]] = relationship(
        "AppointmentModel", back_populates="patient")

    ratings: Mapped[list["RatingModel"]] = relationship(
        "RatingModel", back_populates="patient")

    # one to many
    medical_records: Mapped[list["MedicalRecordModel"]] = relationship(
        back_populates="patient"
    )
    # one to many
    medical_records: Mapped[list["MedicalRecordModel"]] = relationship(
        "MedicalRecordModel", back_populates="patient"
    )

    def __repr__(self):
        return f"<Patient(id={self.id}, first_name='{self.first_name}', last_name='{self.last_name}')>"
