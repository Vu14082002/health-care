from datetime import date
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Date, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.postgresql import Model

if TYPE_CHECKING:
    from src.models.appointment_model import AppointmentModel
    from src.models.doctor_model import DoctorModel
    from src.models.patient_model import PatientModel


# class MedicalModelStatus(enum.Enum):
#     PENDING = "pending"
#     APPROVED = "approved"
#     REJECTED = "rejected"
#     COMPLETED = "completed"


class DrugSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    drug_name: str
    quantity: int
    user_manual: str


class PrescriptionSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    item: list[DrugSchema]


# tien su benh
class MedicalHistoryMine(BaseModel):
    model_config = ConfigDict(extra="forbid")
    allergy: str = ""
    drug: bool = False
    alcohol: bool = False
    cigarette: bool = False
    pipe_tobacco: bool = False
    other: str = ""


class MedicalHistorySchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    mine: MedicalHistoryMine
    family: str | None


# lich su kham benh


class MedicalRecordModel(Model):
    __tablename__ = "medical_record"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    patient_id: Mapped[int] = mapped_column(ForeignKey("patient.id"), nullable=False)

    doctor_create_id: Mapped[int] = mapped_column(ForeignKey("doctor.id"), nullable=False)

    doctor_read_id: Mapped[int] = mapped_column(ForeignKey("doctor.id"), nullable=False)

    appointment_id: Mapped[int] = mapped_column(
        ForeignKey("appointment.id"), nullable=False, unique=True
    )

    # ly do kham benh
    reason: Mapped[str] = mapped_column(Text, nullable=True)

    # Vao ngay thu may cua benh: null True boi vi co the chi di kham suc khoe
    quantity_day_medical: Mapped[int] = mapped_column(Integer, nullable=True)

    # tien su benh
    medical_history: Mapped[MedicalHistorySchema] = mapped_column(JSONB, nullable=False)

    # qua trinh benh ly
    pathological_process: Mapped[str] = mapped_column(Text, nullable=False)

    #  chiu trung benh
    disease_symptoms: Mapped[str] = mapped_column(Text, nullable=True)

    # ton thuong can ban
    basic_disease_damage: Mapped[str] = mapped_column(Text, nullable=True)

    # cac xet nghiem lam san'  can' lam'
    clinical_tests: Mapped[str] = mapped_column(Text, nullable=True)

    main_defense: Mapped[str] = mapped_column(Text, nullable=False, default="")
    secondary_diseases: Mapped[str] = mapped_column(Text, nullable=False, default="")
    treatment_results: Mapped[str] = mapped_column(Text, nullable=False, default="")
    #  tom tat benh
    medical_summary: Mapped[str] = mapped_column(Text, nullable=True)

    # ke hoach dieu tri
    treatment_plan: Mapped[str] = mapped_column(Text, nullable=True)

    # ngat ket thuc dieu tri
    end_date_treatment: Mapped[date] = mapped_column(Date, nullable=False)

    # don thuoc
    prescription: Mapped[PrescriptionSchema] = mapped_column(JSONB, nullable=True)

    # One to One
    appointment: Mapped["AppointmentModel"] = relationship(
        "AppointmentModel", back_populates="medical_record", lazy="joined"
    )

    # Many to one
    patient: Mapped["PatientModel"] = relationship(
        "PatientModel", back_populates="medical_records", lazy="joined"
    )

    # Many to one
    doctor_create: Mapped["DoctorModel"] = relationship(
        "DoctorModel",
        back_populates="medical_records_create",
        lazy="joined",
        foreign_keys=[doctor_create_id],
    )

    doctor_read: Mapped["DoctorModel"] = relationship(
        "DoctorModel",
        back_populates="medical_records_read",
        lazy="joined",
        foreign_keys=[doctor_read_id],
    )
