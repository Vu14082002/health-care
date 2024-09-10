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
    appointment_id: int
    # @validator("end_date_treatment",pre=True)
    # def validate_end_date_treatment(cls, v):
    #     if is


class RequestCreateMedicalRecordsSchema(BaseModel):
    doctor_id: int | None
    appointment_id: int
    reason: str | None
    quantity_day_medical: int | None
    medical_history: MedicalHistorySchema
    pathological_process: str
    disease_symptoms: str | None
    basic_disease_damage: str | None
    clinical_tests: str | None
    medical_summary: str | None
    treatment_plan: str | None
    end_date_treatment: date
    prescription: PrescriptionSchema | None

    # @validator("end_date_treatment",pre=True)
    # def validate_end_date_treatment(cls, v):
    #     if is
