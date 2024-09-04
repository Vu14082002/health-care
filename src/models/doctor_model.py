import email
from typing import TYPE_CHECKING

from sqlalchemy import JSON, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

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


class DoctorModel(Model):
    __tablename__ = "doctor"

    id: Mapped[int] = mapped_column(
        Integer, ForeignKey('user.id'), primary_key=True)

    first_name: Mapped[str] = mapped_column(String, nullable=False)

    last_name: Mapped[str] = mapped_column(String, nullable=False)

    phone_number: Mapped[str] = mapped_column(
        String, nullable=False, unique=True)

    date_of_birth: Mapped[str] = mapped_column(String, nullable=False)

    gender: Mapped[str] = mapped_column(
        String, nullable=False, default="other")

    specialization: Mapped[str] = mapped_column(
        String, nullable=False, default="Dermatology")

    experience_years: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0)

    certifications: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    hopital_address_work: Mapped[str | None] = mapped_column(
        String, nullable=True)

    address: Mapped[str] = mapped_column(String, nullable=False)

    avatar: Mapped[str] = mapped_column(
        Text, nullable=True, default=default_avatar)

    description: Mapped[str] = mapped_column(Text, nullable=True)

    working_schedules: Mapped[list["WorkScheduleModel"]] = relationship(
        "WorkScheduleModel", back_populates="doctor"
    )

    appointments: Mapped[list["AppointmentModel"]] = relationship(
        "AppointmentModel", back_populates="doctor"
    )
    email: Mapped[str] = mapped_column(String, nullable=True, unique=True)

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

    prescriptions: Mapped[list["PrescriptionModel"]] = relationship(
        "PrescriptionModel", back_populates="doctor")
    medical_tests: Mapped[list["MedicalTestModel"]] = relationship(
        "MedicalTestModel", back_populates="doctor")

    def __repr__(self):
        return f"<Doctor(id={self.id}, name='{self.first_name} {self.last_name}', specialization='{self.specialization}', experience_years={self.experience_years})>"
