from typing import TYPE_CHECKING  # type: ignore
from uuid import uuid4

from sqlalchemy import UUID, Column, ForeignKey, Integer, String, Text, event
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.postgresql import Model

if TYPE_CHECKING:
    from src.models.appointment_model import AppointmentModel
    from src.models.billing_model import BillingModel
    from src.models.user import UserModel
else:
    UserModel = "UserModel"

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

    nation: Mapped[str] = mapped_column(String, nullable=False)

    avatar: Mapped[str] = mapped_column(
        __name_pos=Text, nullable=True, default=default_avatar)

    occupation: Mapped[str] = mapped_column(String, nullable=False)

    insurance_number: Mapped[str | None] = mapped_column(String, nullable=True)

    emergancy_contact_number: Mapped[str | None] = mapped_column(
        String, nullable=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    user: Mapped["UserModel"] = relationship(
        "UserModel", uselist=False, back_populates="patient")

    appointments: Mapped["AppointmentModel"] = relationship(
        "AppointmentModel", back_populates="patient")

    billings: Mapped["BillingModel"] = relationship(
        "BillingModel", back_populates="patient")

    def __repr__(self):
        return f"<Patient(id={self.id}, first_name='{self.first_name}', last_name='{self.last_name}')>"
