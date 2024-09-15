import logging as log
from datetime import date, datetime

from sqlalchemy import (Result, Row, and_, asc, case, delete, desc, exists,
                        func, or_, select)
from sqlalchemy.orm import joinedload, selectinload

from src.core.database.postgresql import PostgresRepository
from src.core.exception import BadRequest
from src.enum import ErrorCode
from src.models.appointment_model import AppointmentModel
from src.models.doctor_model import DoctorExaminationPriceModel, DoctorModel
from src.models.patient_model import PatientModel
from src.models.work_schedule_model import WorkScheduleModel
from src.repositories.global_helper_repository import redis_working


class AppointmentRepository(PostgresRepository[AppointmentModel]):
    # start::create_appointment[]
    async def create_appointment(self, patient_id: int, doctor_id: int, work_schedule_id: int, pre_examination_notes: str | None = None):
        try:
            patient_model = await self._get_patient_model_by_id(patient_id)
            doctor_model = await self._get_doctor_model_by_id(doctor_id)
            work_schedule_model = self._get_work_schedule_model_by_id(
                work_schedule_id, doctor_model)
            if work_schedule_model.ordered:
                raise BadRequest(error_code=ErrorCode.ALLREADY_ORDERED.name, errors={
                    "message": "Work schedule is ordered"})
            fee_examprice = self._get_fee_examination(
                doctor_model, work_schedule_model)
            # validate appointment
            appointment = AppointmentModel()
            # logic save redos if online and payment id bank
            # if work_schedule_model.examination_type.lower() == "offline":
            #     appointment.appointment_status = "approved"
            # else:
            #     # FIXME:check logic for online appointment and offline if choose payment id bank
            #     appointment.appointment_status = "pending"
            #     await redis_working.set({"doctor_id": doctor_id, "patient_id": patient_id, "work_schedule_id": work_schedule_id},
            #                             work_schedule_id, 300)
            #     return {"message": "Create appointment successfully"}
            # FXIME: check logic for payment id bank
            appointment.appointment_status = "approved"
            appointment.patient = patient_model
            appointment.doctor = work_schedule_model.doctor
            appointment.work_schedule_id = work_schedule_id
            appointment.doctor_id = doctor_id
            appointment.patient_id = patient_id
            appointment.examination_type = work_schedule_model.examination_type
            appointment.pre_examination_notes = pre_examination_notes if pre_examination_notes else ""
            appointment.total_amount = fee_examprice
            work_schedule_model.ordered = True
            self.session.add(appointment)
            await self.session.flush()
            await self.session.commit()
            await redis_working.set(work_schedule_model.as_dict,
                                    work_schedule_id, 300)
            return {"message": "Create appointment successfully"}
        except (BadRequest) as e:
            log.error(e)
            raise e
        except Exception as e:
            log.error(e)
            raise e

    async def _get_doctor_model_by_id(self, doctor_id: int):
        try:
            query = select(DoctorModel).where(DoctorModel.id == doctor_id).options(
                joinedload(DoctorModel.working_schedules),
                joinedload(DoctorModel.examination_prices)
            )
            result = await self.session.execute(query)
            doctor_model = result.unique().scalar_one_or_none()

            if doctor_model is None:
                raise BadRequest(error_code=ErrorCode.NOT_FOUND.name, errors={
                    "message": "Doctor not found"})
            return doctor_model
        except BadRequest as e:
            log.error(e)
            raise e
        except Exception as e:
            log.error(e)
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

    def _get_work_schedule_model_by_id(self, work_scheduling_id: int, doctor: DoctorModel):
        try:
            for item in doctor.working_schedules:
                if item.id == work_scheduling_id:
                    return item

            raise BadRequest(error_code=ErrorCode.NOT_FOUND.name, errors={
                "message": "Work schedule not found"})
        except BadRequest as e:
            log.error(e)
            raise e
        except Exception as e:
            log.error(e)
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
            # FIXME: LOGIC OT
            if is_online and is_ot:
                fee = ex.online_price * 2
            elif is_online:
                fee = ex.online_price
            elif not is_online and is_ot:
                fee = ex.offline_price * 2
            else:
                fee = ex.offline_price
            return fee
        except BadRequest as e:
            raise e
        except Exception as e:
            raise e
    # end::create_appointment[]

    async def find(self, **kwargs):  # type: ignore
        query = select(self.model_class)
        appointment_status: str = kwargs.get('appointment_status', None)
        from_date: date = kwargs.get('from_date', None)
        to_date: date = kwargs.get('to_date', None)
        examination_type: str = kwargs.get('examination_type', None)
        doctor_name: str = kwargs.get('doctor_name', None)
        patient_name: int = kwargs.get('patient_name', None)
        current_page: int = kwargs.get('current_page', 1)
        page_size: int = kwargs.get('page_size', 10)
        doctor_id: int = kwargs.get('doctor_id', None)
        patient_id: int = kwargs.get('patient_id', None)

        if appointment_status:
            query = query.filter(
                self.model_class.appointment_status == appointment_status)
        if from_date and to_date is None:
            query = query.join(WorkScheduleModel).filter(
                WorkScheduleModel.work_date >= from_date)
        if to_date and from_date is None:
            query = query.join(WorkScheduleModel).filter(
                WorkScheduleModel.work_date <= to_date)
        if from_date and to_date:
            query = query.join(WorkScheduleModel).filter(
                and_(WorkScheduleModel.work_date >= from_date,
                     WorkScheduleModel.work_date <= to_date)
            )
        if examination_type:
            query = query.join(WorkScheduleModel).filter(
                WorkScheduleModel.examination_type == examination_type)
        if doctor_id:
            query = query.filter(self.model_class.doctor_id == doctor_id)
        if patient_id:
            query = query.filter(self.model_class.patient_id == patient_id)
        if doctor_name:
            name_parts = doctor_name.split()
            conditions = [
                or_(
                    self.model_class.doctor.has(
                        DoctorModel.first_name.ilike(f"%{part}%")),
                    self.model_class.doctor.has(
                        DoctorModel.last_name.ilike(f"%{part}%"))
                ) for part in name_parts
            ]
            query = query.join(self.model_class.doctor).filter(
                or_(*conditions)
            )
        if patient_name:
            name_parts = patient_name.split()
            conditions = [
                or_(
                    self.model_class.patient.name.ilike(f"%{part}%")
                ) for part in name_parts
            ]
            query = query.join(self.model_class.patient).filter(
                or_(*conditions)
            )
        # query = query.options(
        #     joinedload(self.model_class.doctor),
        #     joinedload(self.model_class.patient)
        # )
        total_count = await self.session.execute(select(func.count()).select_from(query))
        query = query.offset((current_page - 1) * page_size).limit(page_size)

        result = await self.session.execute(query)
        data = result.scalars().all()
        item = [item.as_dict for item in data]
        total_pages = (total_count.scalar_one() + page_size - 1) // page_size
        return {
            "data": item,
            "current_page": current_page,
            "page_size": page_size,
            "total_pages": total_pages
        }
