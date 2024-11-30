import logging as log
import re
import time
from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Final, Optional

import requests
from sqlalchemy import and_, case, extract, func, insert, or_, select, update
from sqlalchemy.orm import joinedload

from src.config import config
from src.core.database.postgresql import PostgresRepository
from src.core.decorator.exception_decorator import catch_error_repository
from src.core.exception import BadRequest, BaseException, InternalServer
from src.enum import AppointmentModelStatus, ErrorCode
from src.helper.payos_helper import PaymentHelper
from src.models.appointment_model import AppointmentModel, AppointmentModelTypeStatus
from src.models.doctor_model import DoctorExaminationPriceModel, DoctorModel
from src.models.medical_records_model import MedicalRecordModel
from src.models.patient_model import PatientModel
from src.models.payment_model import PaymentModel
from src.models.work_schedule_model import WorkScheduleModel
from src.repositories.global_helper_repository import redis_working

payment_helper=PaymentHelper()

class AppointmentRepository(PostgresRepository[AppointmentModel]):
    # start::create_appointment[]
    @catch_error_repository(message=None)
    async def create_appointment(
        self,
        patient_id: int,
        name: str,
        doctor_id: int,
        work_schedule_id: int,
        pre_examination_notes: str | None = None,
        is_payment: bool = False,
        call_back_url: str | None = None,
        cancel_url:str|None =None
    ):
        if not is_payment:
            raise BadRequest(
                error_code=ErrorCode.PAYMENT_REQUIRED.name,
                errors={"message": ErrorCode.msg_payment_required.value},
            )
        # first check exist appointment with doctor is approved
        appointment_exist = await self.session.execute(
            select(AppointmentModel).where(
                and_(
                    AppointmentModel.patient_id == patient_id,
                    AppointmentModel.appointment_status
                    == AppointmentModelStatus.APPROVED.value,
                )
            )
        )
        appointment_exist = appointment_exist.scalar_one_or_none()
        if appointment_exist:
            raise BadRequest(
                error_code=ErrorCode.YOU_HAVE_NOT_COMPLETE_OTHER_APPOINTMENT.name,
                errors={
                    "message": ErrorCode.msg_you_have_not_complete_other_appointment.value
                },
            )

        # check work schedule is ordered
        patient_model = await self._get_patient_model_by_id(patient_id)
        doctor_model = await self._get_doctor_model_by_id(doctor_id)
        work_schedule_model = self._get_work_schedule_model_by_id(
            work_schedule_id, doctor_model
        )
        if work_schedule_model.ordered:
            raise BadRequest(
                error_code=ErrorCode.ALLREADY_ORDERED.name,
                errors={"message": ErrorCode.msg_appointment_already_order.value},
            )
        fee_examprice = self._get_fee_examination(doctor_model, work_schedule_model)
        # validate appointment
        appointment = AppointmentModel()
        # logic save redos if online and payment id bank
        if work_schedule_model.examination_type.lower() == "online" and not is_payment:
            raise BadRequest(
                error_code=ErrorCode.PAYMENT_REQUIRED.name,
                errors={"message": ErrorCode.msg_payment_required.value},
            )

        # FXIME: check logic for payment id bank
        appointment.appointment_status = AppointmentModelStatus.APPROVED.value
        appointment.name = name
        appointment.patient = patient_model
        appointment.doctor = work_schedule_model.doctor
        appointment.work_schedule_id = work_schedule_id
        appointment.doctor_id = doctor_id
        appointment.patient_id = patient_id
        appointment.examination_type = work_schedule_model.examination_type
        appointment.pre_examination_notes = (
            pre_examination_notes if pre_examination_notes else ""
        )
        appointment.total_amount = fee_examprice
        # 0: update work_schedule_model
        # saving all params to redis
        work_schedule_model.ordered = True
        # 1 save appointment
        self.session.add(appointment)
        # 2:  update medical record by patient data doctor_read_id
        query_update_medical_record_by_patient = (
            update(MedicalRecordModel)
            .where(MedicalRecordModel.patient_id == patient_id)
            .values({"doctor_read_id": doctor_id})
        ).returning(MedicalRecordModel)
        # 3: update doctor_manage_id in patient
        query_update_patient = (
            update(PatientModel)
            .where(PatientModel.id == patient_id)
            .values({"doctor_manage_id": doctor_id})
        ).returning(PatientModel)
        result_medical_record_by_patient = await self.session.execute(
            query_update_medical_record_by_patient
        )
        result_patient_model = await self.session.execute(query_update_patient)
        data_patient = result_patient_model.scalar_one_or_none()
        data_medical_record_by_patient = result_medical_record_by_patient.scalar_one_or_none()
        if not data_patient:
            log.info("Update doctor_manage_id in patient error")
            raise InternalServer(
                error_code=ErrorCode.BAD_REQUEST.name,
                errors={"message": ErrorCode.msg_server_error.value},
            )
        # saving to redis
        if is_payment:
            data = await self._process_payment(
                appoint_model=appointment,
                work_schedule_model=work_schedule_model,
                data_patient=data_patient,
                medical_record_by_patient=data_medical_record_by_patient,
                call_back_url=call_back_url,
                cancel_url=cancel_url
            )
            return data
        await self.session.commit()
        return {"message":ErrorCode.msg_create_appointment_successfully.value}

    @catch_error_repository(message=None)
    async def create_appointment_with_payment(self, payment_id: str,status_code:str):
        MAX_RETRY:Final[int]=3
        obj_payment=payment_helper.get_payment_info(payment_id)
        while obj_payment is None and MAX_RETRY > 0:
            time.sleep(2)
            obj_payment=payment_helper.get_payment_info(payment_id)
            MAX_RETRY-=1
        if not obj_payment:
            raise BadRequest(
                error_code=ErrorCode.BAD_REQUEST.name,
                errors={"message": ErrorCode.msg_payment_not_found.value},
            )
        transactions = obj_payment.get("transactions", [])
        description = transactions[0].get("description")
        match = re.search(r"Ma giao dich (\d+)", description)
        if not match:
            raise BadRequest(
                error_code=ErrorCode.PAYMENT_CONTENT_ERROR.name,
                errors={"message": ErrorCode.msg_payment_content_error.value},
            )
        work_schedule_id = match.group(1)

        value_redis = await redis_working.get(work_schedule_id)
        if not value_redis:
            log.error("Value redis not found")
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            )

        # assign value fot instance
        appointment_data = value_redis.get("appointment")
        del appointment_data["id"]

        patient_id: Final[int] = value_redis.get("patient").get("id")
        work_schedule_id:Final[str]= value_redis.get("work_schedule").get("id")
        insert_appointment= insert(AppointmentModel).values(**appointment_data).returning(AppointmentModel.id)
        update_work_schedule = (
            update(WorkScheduleModel)
            .values({"ordered": True})
            .where(WorkScheduleModel.id == int(work_schedule_id))
        )
        update_patient = (
            update(PatientModel)
            .values(
                {"doctor_manage_id": value_redis.get("patient").get("doctor_manage_id")}
            )
            .where(PatientModel.id == patient_id)
        )
        update_medical_record_by_patient=None
        if value_redis.get("medical_record_by_patient"):
            update_medical_record_by_patient = (
                update(MedicalRecordModel).values(
                    {"doctor_read_id": value_redis.get("medical_record_by_patient").get("doctor_read_id")}
                ).where(MedicalRecordModel.patient_id == patient_id)
            )
        result_appointment =await self.session.execute(insert_appointment)
        appointment_id = result_appointment.scalar_one_or_none()
        if not appointment_id:
            log.error("Insert appointment error")
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            )
        _= await self.session.execute(update_work_schedule)
        _= await self.session.execute(update_patient)
        _= await self.session.execute(update_medical_record_by_patient) if update_medical_record_by_patient else None
        # add instance to session
        payment_model = PaymentModel()
        payment_model.appointment_id = appointment_id
        payment_model.amount = obj_payment.get("amountPaid")
        payment_model.payment_time = datetime.fromisoformat(
            obj_payment.get("createdAt")
        ).replace(tzinfo=None)
        self.session.add(payment_model)
        await redis_working.delete(work_schedule_id)

        # send socket to patient
        url_chat_service = f"{config.BASE_URL_CHAT_SERVICE}/api/payment"
        json_data = {
            "userId": patient_id,
            "isSuccess": True if status_code == "00" else False,
        }
        data = requests.post(url_chat_service, json=json_data)
        if data.status_code != 200:
            log.error("Service chat current not working")
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            )
        if status_code != "00":
            raise BadRequest(
                error_code=ErrorCode.BAD_REQUEST.name,
                errors={"message": ErrorCode.msg_payment_fail.value},
            )

        # send socket to doctor
        url_socket = f"{config.BASE_URL_CHAT_SERVICE}/api/notify/appointment/new"
        _select_work = select(WorkScheduleModel).where(WorkScheduleModel.id == int(work_schedule_id))
        _result_select_work = await self.session.execute(_select_work)
        _work_schedule = _result_select_work.scalar_one()
        data={
            "userId": _work_schedule.doctor_id,
            "fromTime": _work_schedule.start_time.isoformat(),
            "toTime": _work_schedule.end_time.isoformat(),
        }
        result_reponse= requests.post(url_socket, json={"doctor_id": appointment_data.get("doctor_id")})
        if (result_reponse.status_code != 200):
            log.error("Service chat current not working,")

        await self.session.commit()
        return {"message": ErrorCode.msg_create_appointment_successfully.value}

    async def _get_doctor_model_by_id(self, doctor_id: int):
        try:
            query = (
                select(DoctorModel)
                .where(DoctorModel.id == doctor_id)
                .options(
                    joinedload(DoctorModel.working_schedules),
                    joinedload(DoctorModel.examination_prices),
                )
            )
            result = await self.session.execute(query)
            doctor_model = result.unique().scalar_one_or_none()

            if doctor_model is None:
                raise BadRequest(
                    error_code=ErrorCode.NOT_FOUND.name,
                    errors={"message": "Doctor not found"},
                )
            return doctor_model
        except BadRequest as e:
            log.error(e)
            raise e
        except Exception as e:
            log.error(e)
            raise e

    async def _process_payment(
        self,
        appoint_model: AppointmentModel,
        work_schedule_model: WorkScheduleModel,
        data_patient:PatientModel,
        medical_record_by_patient:MedicalRecordModel|None,
        call_back_url,
        cancel_url:str|None=None
    ):
        try:
            work_schedule_id= work_schedule_model.id
            medical_examination_fee = work_schedule_model.medical_examination_fee
            # assign value to for instance
            payos_helper= PaymentHelper()
            data = payos_helper.create_payment(
                amount=int(medical_examination_fee),
                description = f"Ma giao dich {work_schedule_id}.",
                returnUrl=call_back_url,
                cancelUrl=cancel_url,
                time_session=config.MAX_TIME_QR_CODE,
            )
            # save redis
            json_data = {
                "appointment": appoint_model.as_dict,
                "work_schedule":{
                    "id":work_schedule_model.id,
                    "ordered":work_schedule_model.ordered,
                },
                "patient":{
                    "id":data_patient.id,
                    "doctor_manage_id":data_patient.doctor_manage_id
                },
            }
            if  medical_record_by_patient:
                json_data["medical_record_by_patient"] = {
                    "doctor_read_id": medical_record_by_patient.doctor_read_id
                }

            await redis_working.set(
                json_data, str(work_schedule_id), config.MAX_TIME_WORKING_TIME
            )
            if not data:
                raise BadRequest(
                    error_code=ErrorCode.BAD_REQUEST.name,
                    errors={"message": ErrorCode.msg_payment_error.value},
                )
            return data
        except Exception as e:
            log.error(e)
            raise e from e

    async def _get_patient_model_by_id(self, patient_id: int):
        try:
            query = select(PatientModel).where(PatientModel.id == patient_id)
            result = await self.session.execute(query)
            patient_model = result.scalar_one_or_none()

            if patient_model is None:
                log.error("admin send request with patient not found")
                raise BadRequest(
                    error_code=ErrorCode.NOT_FOUND.name,
                    errors={"message": ErrorCode.msg_patient_not_found.value},
                )
            return patient_model
        except BadRequest as e:
            raise e
        except Exception as e:
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            )from e

    def _get_work_schedule_model_by_id(
        self, work_scheduling_id: int, doctor: DoctorModel
    ):
        try:
            for item in doctor.working_schedules:
                if item.id == work_scheduling_id:
                    return item

            raise BadRequest(
                error_code=ErrorCode.NOT_FOUND.name,
                errors={"message": "Work schedule not found"},
            )
        except BadRequest as e:
            log.error(e)
            raise e
        except Exception as e:
            log.error(e)
            raise e

    def _get_fee_examination(
        self, doctor: DoctorModel, work_scheduling: WorkScheduleModel
    ):
        try:
            if len(doctor.examination_prices) == 0:
                raise BadRequest(
                    error_code=ErrorCode.NOT_FOUND.name,
                    errors={
                        "message": "Doctor examination price not found, data maybe is invalid"
                    },
                )
            ex: DoctorExaminationPriceModel = doctor.examination_prices[0]
            is_ot = not (8 <= work_scheduling.start_time.hour <= 17)
            is_online = work_scheduling.examination_type.lower() == "online"
            fee = 0.0
            if is_online and is_ot:
                fee = ex.online_price * 2
            elif is_online:
                fee = ex.online_price
            elif not is_online and is_ot:
                fee = ex.offline_price * 2
            else:
                fee = ex.offline_price
            return fee
        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            ) from e

    # end::create_appointment[]
    @catch_error_repository(message=None)
    async def find(self, **kwargs):  # type: ignore
        query = select(self.model_class)
        appointment_status: str = kwargs.get("appointment_status", None)
        from_date: date = kwargs.get("from_date", None)
        to_date: date = kwargs.get("to_date", None)
        examination_type: str = kwargs.get("examination_type", None)
        doctor_name: str = kwargs.get("doctor_name", None)
        patient_name: int = kwargs.get("patient_name", None)
        current_page: int = kwargs.get("current_page", 1)
        page_size: int = kwargs.get("page_size", 10)
        doctor_id: int = kwargs.get("doctor_id", None)
        patient_id: int = kwargs.get("patient_id", None)
        is_join_work_schedule_model = True
        if appointment_status:
            query = query.filter(
                self.model_class.appointment_status == appointment_status
            )
        if from_date and to_date is None:
            query = query.join(WorkScheduleModel).filter(
                WorkScheduleModel.work_date >= from_date
            )
        elif to_date and from_date is None:
            query = query.join(WorkScheduleModel).filter(
                WorkScheduleModel.work_date <= to_date
            )
        elif from_date and to_date:
            query = query.join(WorkScheduleModel).filter(
                and_(
                    WorkScheduleModel.work_date >= from_date,
                    WorkScheduleModel.work_date <= to_date,
                )
            )
        else:
            is_join_work_schedule_model = False
        if examination_type:
            if is_join_work_schedule_model:
                query = query.filter(
                    WorkScheduleModel.examination_type == examination_type
                )
            else:
                query = query.join(WorkScheduleModel).filter(
                    WorkScheduleModel.examination_type == examination_type
                )
        if doctor_id:
            query = query.filter(self.model_class.doctor_id == doctor_id)
        if patient_id:
            query = query.filter(self.model_class.patient_id == patient_id)
        if doctor_name:
            name_parts = doctor_name.split()
            conditions = [
                or_(
                    self.model_class.doctor.has(
                        DoctorModel.first_name.ilike(f"%{part}%")
                    ),
                    self.model_class.doctor.has(
                        DoctorModel.last_name.ilike(f"%{part}%")
                    ),
                )
                for part in name_parts
            ]
            query = query.join(self.model_class.doctor).filter(or_(*conditions))
        if patient_name:
            name_parts = patient_name.split()
            conditions = [
                or_(self.model_class.patient.name.ilike(f"%{part}%"))
                for part in name_parts
            ]
            query = query.join(self.model_class.patient).filter(or_(*conditions))
        total_count = await self.session.execute(
            select(func.count()).select_from(query)
        )
        query = query.offset((current_page - 1) * page_size).limit(page_size)

        result = await self.session.execute(query)
        data = result.scalars().all()
        items = []

        for item in data:
            dict_item = item.as_dict
            dict_item["is_payment"] = True if item.payment else False
            dict_item["work_schedule"] = item.work_schedule.as_dict
            if doctor_id:
                dict_item["work_schedule"].update(
                    {
                        "patient": {
                            "first_name": item.patient.first_name,
                            "last_name": item.patient.last_name,
                            "avatar": item.patient.avatar,
                            "phone_number": item.patient.phone_number,
                        }
                    }
                )
            elif patient_id:
                dict_item["work_schedule"].update(
                    {
                        "doctor": {
                            "first_name": item.doctor.first_name,
                            "last_name": item.doctor.last_name,
                            "certification": item.doctor.certification,
                            "specialization": item.doctor.specialization,
                            "avatar": item.doctor.avatar,
                            "phone_number": item.doctor.phone_number,
                        }
                    }
                )
            else:
                dict_item["work_schedule"].update(
                    {
                        "patient": {
                            "first_name": item.patient.first_name,
                            "last_name": item.patient.last_name,
                            "avatar": item.patient.avatar,
                            "phone_number": item.patient.phone_number,
                        }
                    }
                )
                dict_item["work_schedule"].update(
                    {
                        "doctor": {
                            "first_name": item.doctor.first_name,
                            "last_name": item.doctor.last_name,
                            "certification": item.doctor.certification,
                            "specialization": item.doctor.specialization,
                            "avatar": item.doctor.avatar,
                            "phone_number": item.doctor.phone_number,
                        }
                    }
                )
            items.append(dict_item)

        total_pages = (total_count.scalar_one() + page_size - 1) // page_size
        return {
            "data": items,
            "current_page": current_page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    @catch_error_repository(message=None)
    async def delete_appointment(self, appointment_id: int, patient_id: int):
        statment_appointment =select(AppointmentModel).where(
            AppointmentModel.patient_id == patient_id,
            AppointmentModel.id == appointment_id,
        ).options(
            joinedload(AppointmentModel.work_schedule)
        )
        result_appointment = await self.session.execute(statment_appointment)
        appointment = result_appointment.scalar_one_or_none()
        if appointment is None:
            raise BadRequest(
                error_code=ErrorCode.BAD_REQUEST.name,
                errors={"message": ErrorCode.msg_not_found_appointment.value},
            )
        if appointment.appointment_status == AppointmentModelStatus.COMPLETED.value:
            raise BadRequest(
                error_code=ErrorCode.BAD_REQUEST.name,
                errors={
                    "message": ErrorCode.msg_not_caceled_appointment_alrealdy_finish.value
                },
            )
        working_date = appointment.work_schedule.work_date
        working_time = appointment.work_schedule.start_time
        date_time_working = datetime.combine(working_date, working_time)
        current_time = datetime.now()
        time_diff = date_time_working - current_time
        if time_diff <= timedelta(hours=48):
            raise BadRequest(
                error_code=ErrorCode.BAD_REQUEST.name,
                errors={
                    "message": ErrorCode.msg_not_caceled_appointment_less_than_48_hours.value
                },
            )
        appointment.work_schedule.ordered = False
        await self.session.delete(appointment)
        await self.session.commit()
        return {"message": ErrorCode.msg_delete_appointment_successfully.value}

    @catch_error_repository(message=None)
    async def statistical_appointment(self, year: int):
        current_month = datetime.now().month +1
        current_year = datetime.now().year
        # months = (
        #     list(range(1, current_month))
        #     if year == current_year
        #     else list(range(1, 13))
        # )
        months = list(range(1, 13))

        query = (
            select(
                func.count(AppointmentModel.appointment_status),
                AppointmentModel.appointment_status,
                extract("month", func.to_timestamp(AppointmentModel.created_at)).label(
                    "month"
                ),
                extract("year", func.to_timestamp(AppointmentModel.created_at)).label(
                    "year"
                ),
            )
            .where(extract("year", func.to_timestamp(AppointmentModel.created_at)) == year)
            .group_by(AppointmentModel.appointment_status, "month", "year")
            .order_by("year", "month", AppointmentModel.appointment_status)
        )

        result = await self.session.execute(query)
        data = result.all()

        appointment_status_by_year = defaultdict(
            lambda: defaultdict(lambda: defaultdict(int))
        )

        for month in months:
            for status in AppointmentModelStatus.all_statuses():
                appointment_status_by_year[str(year)][str(month)][status] = 0

        for count, status, month, year in data:
            status_enum = AppointmentModelStatus(status).value
            year_str = str(year).split(".")[0]
            month_str = str(month).split(".")[0]
            appointment_status_by_year[year_str][month_str][status_enum] = count

        return appointment_status_by_year

    @catch_error_repository(message=None)
    async def statistical_price(self, year: Optional[int]):
        data_response = {
            "today_price": {
                "total_price": 0,
                "online_price": 0,
                "offline_price": 0,
            },
            "previous_price": {
                "total_price": 0,
                "online_price": 0,
                "offline_price": 0,
            },
            "monthly_price": {
                "total_price": 0,
                "online_price": 0,
                "offline_price": 0,
            },
            "yearly_price": {
                "total_price": 0,
                "online_price": 0,
                "offline_price": 0,
            },
            "monthly_details": {month: {
                "total_price": 0,
                "online_price": 0,
                "offline_price": 0,
            } for month in range(1, 13)},
        }

        today = datetime.now()
        yesterday = today - timedelta(days=1)

        def build_price_query(day=None, month=None, year=None):
            """Helper function to build query based on given day, month, and year."""
            filters = [AppointmentModel.appointment_status == AppointmentModelStatus.COMPLETED.value]
            if year:
                filters.append(extract("year", WorkScheduleModel.work_date) == year)
            if month:
                filters.append(extract("month", WorkScheduleModel.work_date) == month)
            if day:
                filters.append(extract("day", WorkScheduleModel.work_date) == day)

            total_price = func.sum(WorkScheduleModel.medical_examination_fee).label("total_price")

            online_price = func.sum(
                    case(
                        (
                            WorkScheduleModel.examination_type == AppointmentModelTypeStatus.ONLINE.value,
                            WorkScheduleModel.medical_examination_fee,
                        ),
                        else_=0,
                    )
                ).label("online_price")

            offline_price = func.sum(
                case(
                    (
                        WorkScheduleModel.examination_type
                        == AppointmentModelTypeStatus.OFFLINE.value,
                        WorkScheduleModel.medical_examination_fee,
                    ),
                    else_=0,
                )
            ).label("offline_price")

            return (
                select(total_price, online_price, offline_price)
                .join(AppointmentModel)
                .where(*filters)
            )

        # Doanh thu hôm nay
        result_today_price = await self.session.execute(build_price_query(day=today.day, month=today.month, year=today.year))
        today_price_data = result_today_price.fetchone()
        if today_price_data:
            data_response["today_price"]["total_price"] = today_price_data.total_price or 0
            data_response["today_price"]["online_price"] = today_price_data.online_price or 0
            data_response["today_price"]["offline_price"] = today_price_data.offline_price or 0

        # Doanh thu hôm trước
        result_previous_price = await self.session.execute(build_price_query(day=yesterday.day, month=yesterday.month, year=yesterday.year))
        previous_price_data = result_previous_price.fetchone()
        if previous_price_data:
            data_response["previous_price"]["total_price"] = previous_price_data.total_price or 0
            data_response["previous_price"]["online_price"] = previous_price_data.online_price or 0
            data_response["previous_price"]["offline_price"] = previous_price_data.offline_price or 0

        # Doanh thu tháng hiện tại
        result_monthly_price = await self.session.execute(build_price_query(month=today.month, year=today.year))
        monthly_price_data = result_monthly_price.fetchone()
        if monthly_price_data:
            data_response["monthly_price"]["total_price"] = monthly_price_data.total_price or 0
            data_response["monthly_price"]["online_price"] = monthly_price_data.online_price or 0
            data_response["monthly_price"]["offline_price"] = monthly_price_data.offline_price or 0

        # Doanh thu từng tháng trong năm
        for month in range(1, 13):
            if not year:
                year = today.year
            result_month_detail = await self.session.execute(build_price_query(month=month, year=year))
            month_detail_data = result_month_detail.fetchone()
            if month_detail_data:
                data_response["monthly_details"][month]["total_price"] = month_detail_data.total_price or 0
                data_response["monthly_details"][month]["online_price"] = month_detail_data.online_price or 0
                data_response["monthly_details"][month]["offline_price"] = month_detail_data.offline_price or 0

        # Tổng doanh thu năm
        data_response["yearly_price"]["total_price"] = sum(
            data_response["monthly_details"][month]["total_price"] for month in range(1, 13)
        )
        data_response["yearly_price"]["online_price"] = sum(
            data_response["monthly_details"][month]["online_price"] for month in range(1, 13)
        )
        data_response["yearly_price"]["offline_price"] = sum(
            data_response["monthly_details"][month]["offline_price"] for month in range(1, 13)
        )

        return data_response

    @catch_error_repository(message=None)
    async def statistical_price_person(self,from_date:date, to_date:date , user_id, *args,**kwargs):
        # convert date to datetime
        from_date = datetime.combine(from_date, datetime.min.time())
        to_date = datetime.combine(to_date, datetime.max.time())
        _select_payment = (
            select(func.sum(PaymentModel.amount).label("total_price"))
            .join(AppointmentModel)
            .where(
                or_(
                    AppointmentModel.doctor_id == user_id,
                    AppointmentModel.patient_id == user_id
                ),
                PaymentModel.payment_time >= from_date,
                PaymentModel.payment_time <= to_date
            )
        )
        _result_payment = await self.session.execute(_select_payment)
        _total_payment = _result_payment.scalar_one()
        if not _total_payment:
            _total_payment = 0
        return {"total_price": _total_payment,"from_date":from_date.isoformat(),"to_date":to_date.isoformat()}

    @catch_error_repository(message=None)
    async def statistical_price_all_doctor(self,from_date:date, to_date:date):
        # convert date to datetime
        from_date = datetime.combine(from_date, datetime.min.time())
        to_date=datetime.combine(to_date, datetime.max.time())
        _query = (
            select(
                DoctorModel,
                func.coalesce(func.sum(PaymentModel.amount), 0).label("total_price"),
            )
            .select_from(DoctorModel)  # Xác định bảng chính
            .outerjoin(AppointmentModel, AppointmentModel.doctor_id == DoctorModel.id)
            .outerjoin(PaymentModel, PaymentModel.appointment_id == AppointmentModel.id)
            .where(
                (PaymentModel.payment_time.is_(None)) |
                ((PaymentModel.payment_time >= from_date) & (PaymentModel.payment_time <= to_date))
            )
            .group_by(DoctorModel)
        )


        _result_statment = await self.session.execute(_query)
        _data_result = _result_statment.all()
        _include_field_doctor=["id","first_name","last_name","certification","specialization","phone_number","date_of_birth","gender","type_of_disease","is_local_person"]
        data = []

        for item in _data_result:
            doctor_model = item[0]
            _total_price = item[1]
            _doctor_data = doctor_model.as_dict
            # remove field
            for key in list(_doctor_data.keys()):
                if key not in _include_field_doctor:
                    del _doctor_data[key]
            _doctor_data["total_price"] = _total_price
            data.append(_doctor_data)
        return data

    @catch_error_repository(message=None)
    async def statistical_price_all_patients(self,from_date:date, to_date:date):
        # convert date to datetime
        from_date = datetime.combine(from_date, datetime.min.time())
        to_date=datetime.combine(to_date, datetime.max.time())
        _query = (
            select(
                PatientModel,
                func.coalesce(func.sum(PaymentModel.amount), 0).label("total_price"),
            )
            .select_from(PatientModel)  # Xác định bảng chính
            .outerjoin(AppointmentModel, AppointmentModel.patient_id == PatientModel.id)
            .outerjoin(PaymentModel, PaymentModel.appointment_id == AppointmentModel.id)
            .where(
                (PaymentModel.payment_time.is_(None)) |
                ((PaymentModel.payment_time >= from_date) & (PaymentModel.payment_time <= to_date))
            )
            .group_by(PatientModel)
        )


        _result_statment = await self.session.execute(_query)
        _data_result = _result_statment.all()
        _include_field_patients=["id","first_name","last_name","phone_number","date_of_birth","gender","email","address","emergancy_contact_number"]
        data = []

        for item in _data_result:
            patient_model = item[0]
            _total_price = item[1]
            _patient_data = patient_model.as_dict
            # remove patient_model
            for key in list(_patient_data.keys()):
                if key not in _include_field_patients:
                    del _patient_data[key]
            _patient_data["total_price"] = _total_price
            data.append(_patient_data)
        return data
