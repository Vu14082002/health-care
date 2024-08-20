from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.postgresql import Model


class DoctorModel(Model):
    __tablename__ = "doctor"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)

    first_name: Mapped[str] = mapped_column(String(255), nullable=False)

    last_name: Mapped[str] = mapped_column(String(255), nullable=False)

    specialization: Mapped[str] = mapped_column(String(255), nullable=False)

    schedule: Mapped[str] = mapped_column(Text, nullable=True)

    appointments: Mapped["AppointmentModel"] = relationship(
        "AppointmentModel", back_populates="doctor")

    def __repr__(self):
        return f"<Doctor(id={self.id}, first_name='{self.first_name}', last_name='{self.last_name}', specialization='{self.specialization}')>"
