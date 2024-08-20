from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.postgresql import Model

default_avatar = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQS0iv-HzCTjY2RQ7JLiYe23Rw2Osp-n9PqUg&s"


class DoctorModel(Model):
    __tablename__ = "doctor"

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

    appointments: Mapped["AppointmentModel"] = relationship(
        "AppointmentModel", back_populates="doctor")

    def __repr__(self):
        return f"<Doctor(id={self.id}, first_name='{self.first_name}', last_name='{self.last_name}', specialization='{self.specialization}')>"
