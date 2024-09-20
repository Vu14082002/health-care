import json
from datetime import date, datetime, time, timedelta
from math import e
from typing import Annotated, List, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
    validator,
)
from starlette.datastructures import UploadFile
from typing_extensions import Any, Literal

from src.models.medical_records_model import (
    DrugSchema,
    MedicalHistoryMine,
    MedicalHistorySchema,
    PrescriptionSchema,
)


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
    appointment_id: int = Field(description="Id cuộc hẹn", examples=[1])
    reason: Optional[str] = Field(
        description="Lý do khám bệnh", examples=["Đã tới bị đau"]
    )
    quantity_day_medical: Optional[int] = Field(
        description="Vào ngày thứ mấy của bệnh", examples=[10]
    )
    medical_history: MedicalHistorySchema = Field(description="Tiền sử bệnh")
    pathological_process: str = Field(default="", description="Quá trình bệnh lý")
    disease_symptoms: Optional[str] = Field(default="", description="Triệu chứng bệnh")
    basic_disease_damage: Optional[str] = Field(
        default="", description="Tổn thương căn bản"
    )
    clinical_tests: Optional[str] = Field(
        default="", description="Các xét nghiệm lâm sàng cần làm"
    )
    medical_summary: Optional[str] = Field(default="", description="Tóm tắt bệnh")
    treatment_plan: Optional[str] = Field(default="", description="Kế hoạch điều trị")
    end_date_treatment: date = Field(
        default=datetime.now().date(), description="Ngày kết thúc điều trị"
    )
    main_defense: str = Field(default="", description="Bệnh chính")
    secondary_diseases: Optional[str] = Field(default="", description="Các bệnh phụ")
    treatment_results: str = Field(default="", description="Kết quả điều trị")
    prescription: Optional[PrescriptionSchema] = Field(
        default=None, description="Đơn thuốc"
    )

    class Config:
        json_encoders = {date: lambda v: v.isoformat()}

    # Uncomment and complete this validator if needed
    # @validator("end_date_treatment", pre=True)
    # def validate_end_date_treatment(cls, v):
    #     if v < datetime.now().date():
    #         raise ValueError("End date of treatment cannot be in the past.")
    #     return v


class RequestUpdateMedicalRecordsSchema(BaseModel):
    id: int = Field(description="Id bản ghi", examples=[1])
    reason: Optional[str] = Field(
        description="Lý do khám bệnh", examples=["Đã tới bị đau"]
    )
    quantity_day_medical: Optional[int] = Field(
        description="Vào ngày thứ mấy của bệnh", examples=[10]
    )
    medical_history: MedicalHistorySchema = Field(description="Tiền sử bệnh")
    pathological_process: str = Field(default="", description="Quá trình bệnh lý")
    disease_symptoms: Optional[str] = Field(default="", description="Triệu chứng bệnh")
    basic_disease_damage: Optional[str] = Field(
        default="", description="Tổn thương căn bản"
    )
    clinical_tests: Optional[str] = Field(
        default="", description="Các xét nghiệm lâm sàng cần làm"
    )
    medical_summary: Optional[str] = Field(default="", description="Tóm tắt bệnh")
    treatment_plan: Optional[str] = Field(default="", description="Kế hoạch điều trị")
    end_date_treatment: date = Field(
        default=datetime.now().date(), description="Ngày kết thúc điều trị"
    )
    main_defense: str = Field(default="", description="Bệnh chính")
    secondary_diseases: Optional[str] = Field(default="", description="Các bệnh phụ")
    treatment_results: str = Field(default="", description="Kết quả điều trị")
    prescription: Optional[PrescriptionSchema] = Field(
        default=None, description="Đơn thuốc"
    )

    class Config:
        json_encoders = {date: lambda v: v.isoformat()}


class RequestGetAppointmentByIdSchema(BaseModel):
    appointment_id: int
