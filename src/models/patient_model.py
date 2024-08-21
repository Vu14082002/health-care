from typing import TYPE_CHECKING
from uuid import uuid4

from regex import D
from sqlalchemy import UUID, Column, ForeignKey, Integer, String, Text, event
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.postgresql import Model

if TYPE_CHECKING:
    from src.models.appointment_model import AppointmentModel
    from src.models.dermatology_medical import DermatologyMedicalRecords
    from src.models.medical_model import MedicalModel
    from src.models.rating_model import RatingModel
    from src.models.user import UserModel

default_avatar = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSn5k7ItLSv5Rd7mdIOYQyPuvfr26Q5cdjk2AMGgw3wnBLmZ5LTOUsXh0jQ92RgRGx8G6g&usqp=CAU"


def gen_uuid() -> str:
    return str(uuid4())


class PatientModel(Model):
    __tablename__ = "patient"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    first_name: Mapped[str] = mapped_column(String, nullable=False)

    last_name: Mapped[str] = mapped_column(String, nullable=False)

    date_of_birth: Mapped[str] = mapped_column(String, nullable=False)

    gender: Mapped[str] = mapped_column(
        String, nullable=False, default="other")

    phone_number: Mapped[str] = mapped_column(
        String, nullable=False, unique=True)

    address: Mapped[str] = mapped_column(String, nullable=False)

    nation: Mapped[str] = mapped_column(String, nullable=True)

    avatar: Mapped[str] = mapped_column(
        __name_pos=Text, nullable=True, default=default_avatar)

    occupation: Mapped[str] = mapped_column(String, nullable=False)

    emergancy_contact_number: Mapped[str | None] = mapped_column(
        String, nullable=True)

    insurance_number: Mapped[str | None] = mapped_column(String, nullable=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    user: Mapped["UserModel"] = relationship(
        "UserModel", uselist=False, back_populates="patient")

    appointments: Mapped[list["AppointmentModel"]] = relationship(
        "AppointmentModel", back_populates="patient")

    dermatology_records: Mapped[list["DermatologyMedicalRecords"]] = relationship(
        "DermatologyMedicalRecords", back_populates="patient")
    ratings: Mapped[list["RatingModel"]] = relationship(
        "RatingModel", back_populates="patient")

    def __repr__(self):
        return f"<Patient(id={self.id}, first_name='{self.first_name}', last_name='{self.last_name}')>"
