import re

from sqlalchemy import (Result, Row, and_, asc, case, delete, desc, exists,
                        func, or_, select)
from sqlalchemy.orm import selectinload
from tomlkit import aot

from src.core.database.postgresql import PostgresRepository
from src.core.exception import BadRequest
from src.enum import ErrorCode
from src.models.appointment_model import AppointmentModel
from src.models.doctor_model import DoctorExaminationPriceModel, DoctorModel
from src.models.patient_model import PatientModel
from src.models.work_schedule_model import WorkScheduleModel


class AppointmentRepository(PostgresRepository[AppointmentModel]):
    # start::create_appointment[]
    async def create_appointment(self, patient_id: int, doctor_id: int, work_schedule_id: int, pre_examination_notes: str | None = None):
        try:
            patient_model = await self._get_patient_model_by_id(patient_id)
            doctor_model = await self._get_doctor_model_by_id(doctor_id)
            work_schedule_model = await self._get_work_schedule_model_by_id(
                work_schedule_id, doctor_model)
            fee_examprice = self._get_fee_examination(
                doctor_model, work_schedule_model)
            appointment = AppointmentModel()
            appointment.appointment_date_start = work_schedule_model.start_time
            appointment.appointment_date_end = work_schedule_model.end_time
            appointment.patient = patient_model
            appointment.doctor = work_schedule_model.doctor
            appointment.appointment_status = "approved" if work_schedule_model.examination_type.lower(
            ) == "offline" else "pending"
            appointment.examination_type = work_schedule_model.examination_type
            appointment.pre_examination_notes = pre_examination_notes if pre_examination_notes else ""
            appointment.total_amount = fee_examprice
            self.session.add(appointment)
            await self.session.commit()
            return {"message": "Create appointment successfully"}
        except (BadRequest) as e:
            raise e
        except Exception as e:
            raise e

    async def _get_doctor_model_by_id(self, doctor_id: int):
        try:
            query = select(DoctorModel).where(DoctorModel.id == doctor_id).options(
                selectinload(DoctorModel.examination_prices))
            result = await self.session.execute(query)
            doctor_model = result.scalar_one_or_none()

            if doctor_model is None:
                raise BadRequest(error_code=ErrorCode.NOT_FOUND.name, errors={
                    "message": "Doctor not found"})
            return doctor_model
        except BadRequest as e:
            raise e
        except Exception as e:
            raise e

    async def _get_patient_model_by_id(self, patient_id: int):
        try:
            query = select(PatientModel).where(PatientModel.id == patient_id)
            result = await self.session.execute(query)
            patient_model = result.scalar_one_or_none()

            if patient_model is None:
                raise BadRequest(error_code=ErrorCode.NOT_FOUND.name, errors={
                    "message": "Patient not found"})
            return patient_model
        except BadRequest as e:
            raise e
        except Exception as e:
            raise e

    async def _get_work_schedule_model_by_id(self, work_scheduling_id: int, doctor: DoctorModel):
        try:
            for item in doctor.working_schedules:
                if item.id == work_scheduling_id:
                    return item

            raise BadRequest(error_code=ErrorCode.NOT_FOUND.name, errors={
                "message": "Work schedule not found"})
        except BadRequest as e:
            raise e
        except Exception as e:
            raise e

    def _get_fee_examination(self, doctor: DoctorModel, work_scheduling: WorkScheduleModel):
        try:
            if len(doctor.examination_prices) == 0:
                raise BadRequest(error_code=ErrorCode.NOT_FOUND.name, errors={
                    "message": "Doctor examination price not found, data maybe is invalid"})
            ex: DoctorExaminationPriceModel = doctor.examination_prices[0]
            is_ot = not (8 <= work_scheduling.start_time.hour <= 17)
            is_online = work_scheduling.examination_type.lower() == "online"
            fee = 0.0
            if is_online and is_ot:
                fee = ex.online_price * ex.ot_price_fee
            elif is_online:
                fee = ex.online_price
            elif not is_online and is_ot:
                fee = ex.offline_price * ex.ot_price_fee
            else:
                fee = ex.offline_price
            return fee
        except BadRequest as e:
            raise e
        except Exception as e:
            raise e
    # end::create_appointment[]
