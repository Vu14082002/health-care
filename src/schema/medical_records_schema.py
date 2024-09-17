import json
from datetime import date, datetime, time, timedelta
from typing import Annotated, List, Optional

from pydantic import (BaseModel, ConfigDict, Field, field_validator,
                      model_validator, validator)
from starlette.datastructures import UploadFile
from typing_extensions import Any, Literal

from src.models.medical_records_model import (DrugSchema, MedicalHistoryMine,
                                              MedicalHistorySchema,
                                              PrescriptionSchema)


class RequestGetAllMedicalRecordsSchema(BaseModel):
    start_date: Optional[date]
    end_date: Optional[date]
    current_page: int = Field(default=1)
    page_size: int = Field(default=10)

    class Config:
        json_encoders = {date: lambda v: v.isoformat()}


# class RequestGetAllMedicalRecordsSchema(BaseModel):
#     doctor_id: int | None
#     patient_id: int | None
#     start_date: date | None
#     end_date: date | None
#     current_page: Optional[int] = Field(default=1)
#     page_size: Optional[int] = Field(default=10)

#     class Config:
#         json_encoders = {date: lambda v: v.isoformat()}


class RequestCreateMedicalRecordsSchema(BaseModel):
    appointment_id: int = Field(description="Id cuoc hen")
    reason: str | None = Field(description="Ly kham benh")
    quantity_day_medical: int | None = Field(
        description="Vao ngay thu may cua benh")
    medical_history: MedicalHistorySchema = Field(description="Tien su benh")
    pathological_process: str = Field(
        default="", description="Qua trinh benh ly")
    disease_symptoms: str | None = Field(
        default="", description="Chiu trung benh")
    basic_disease_damage: str | None = Field(
        default="", description="Ton thuong can ban")
    clinical_tests: str | None = Field(
        default="", description="Cac xet nghiem lam san'  can' lam'")
    medical_summary: str | None = Field(default="", description="Tom tat benh")
    treatment_plan: str | None = Field(
        default="", description="Ke hoach dieu tri")
    end_date_treatment: date = Field(
        default=datetime.now().date(), description="Ngay ket thuc dieu tri")
    main_defense: str = Field(default="", description="Benh chinh")
    secondary_diseases: str | None = Field(
        default="", description="Cac benh phu")
    treatment_results: str = Field(default="", description="Ket qua dieu tri")
    prescription: PrescriptionSchema | None = Field(
        default=None, description="Don thuoc")

    class Config:
        json_encoders = {date: lambda v: v.isoformat()}
    # @validator("end_date_treatment", pre=True)
    # def validate_end_date_treatment(cls, v):
    #     if is
