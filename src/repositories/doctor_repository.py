import logging
import math
from collections import defaultdict
from curses.ascii import isdigit
from datetime import date, datetime, time, timedelta
from re import M
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Tuple

from regex import B
from sqlalchemy import (Result, Row, and_, asc, case, delete, desc, exists,
                        func, not_, or_, select)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from src.config import config
from src.core.cache.redis_backend import RedisBackend
from src.core.database.postgresql import PostgresRepository
from src.core.exception import BadRequest, Forbidden
from src.core.security.password import PasswordHandler
from src.enum import ErrorCode
from src.models import work_schedule_model
from src.models.appointment_model import AppointmentModel
from src.models.doctor_model import (DoctorExaminationPriceModel, DoctorModel,
                                     TypeOfDisease)
from src.models.medical_records_model import MedicalRecordModel
from src.models.rating_model import RatingModel
from src.models.user_model import Role, UserModel
from src.models.work_schedule_model import WorkScheduleModel
from src.repositories.global_func import destruct_where, process_orderby
from src.repositories.global_helper_repository import redis_working
from src.schema.doctor_schema import RequestDoctorWorkScheduleNextWeek
from src.schema.register import RequestRegisterDoctorSchema


class DoctorRepository(PostgresRepository[DoctorModel]):

    async def get_all(self, skip: int = 0, limit: int = 10, join_: Optional[set[str]] = None,
                      where: Optional[Dict[str, Any]] = None, order_by: Optional[Dict[str, str]] = None,
                      min_avg_rating: Optional[float] = None, min_rating_count: Optional[int] = None) -> List[Dict[str, Any]]:
        try:
            condition = destruct_where(self.model_class, where or {})
            # subquery to get avg_rating and rating_count
            subquery = (
                select(
                    RatingModel.doctor_id,
                    func.avg(RatingModel.rating).label('avg_rating'),
                    func.count(RatingModel.id).label('rating_count')
                )
                .group_by(RatingModel.doctor_id)
                .subquery()
            )
            # subquery to get latest examination price
            latest_price_subquery = (
                select(
                    DoctorExaminationPriceModel.id,
                    DoctorExaminationPriceModel.doctor_id,
                    DoctorExaminationPriceModel.online_price,
                    DoctorExaminationPriceModel.offline_price,
                    DoctorExaminationPriceModel.created_at,
                )
                .distinct(DoctorExaminationPriceModel.doctor_id)
                .order_by(
                    DoctorExaminationPriceModel.doctor_id,
                    desc(DoctorExaminationPriceModel.created_at)
                )
                .subquery()
            )

            current_date = datetime.now().date()
            current_time = datetime.now().time()
            start_date = current_date
            end_date = start_date + timedelta(days=(6 - start_date.weekday()))
            # if current_date.weekday() < 1:
            #     start_date = current_date + \
            #         timedelta(days=(1 - current_date.weekday()) % 7)
            # end_date = start_date + \
            #     timedelta(days=(6 - start_date.weekday()) % 7)
            # key in redis
            ids = []
            key: List[str] = await redis_working.get_all_keys()
            if key:
                for k in key:
                    if k.isdigit():
                        ids.append(int(k))
            work_schedule_subquery = (
                select(
                    WorkScheduleModel.doctor_id,
                    func.json_agg(
                        func.json_build_object(
                            "id", WorkScheduleModel.id,
                            'work_date', WorkScheduleModel.work_date,
                            'start_time', WorkScheduleModel.start_time,
                            'end_time', WorkScheduleModel.end_time,
                            'examination_type', WorkScheduleModel.examination_type,
                            "medical_examination_fee", WorkScheduleModel.medical_examination_fee,
                            "ordered", WorkScheduleModel.ordered
                        )
                    ).label('work_schedules')
                )
                .where(
                    WorkScheduleModel.work_date.between(start_date, end_date),
                    # FIXME for redis
                    # WorkScheduleModel.id.not_in(ids),
                    # FIXMEL: if tesst post men comemnt this code to test
                    not_(
                        and_(
                            WorkScheduleModel.work_date == current_date,
                            WorkScheduleModel.start_time < current_time
                        )
                    )
                )
                .group_by(WorkScheduleModel.doctor_id)
                .subquery()
            )
            query = (
                select(
                    self.model_class,
                    case(
                        (subquery.c.avg_rating != None, subquery.c.avg_rating),
                        else_=0.0
                    ).label('avg_rating'),
                    case(
                        (subquery.c.rating_count != None, subquery.c.rating_count),
                        else_=0
                    ).label('rating_count'),
                    latest_price_subquery,
                    work_schedule_subquery.c.work_schedules
                )
                .outerjoin(subquery, self.model_class.id == subquery.c.doctor_id)
                .outerjoin(latest_price_subquery, self.model_class.id == latest_price_subquery.c.doctor_id)
                .outerjoin(work_schedule_subquery, self.model_class.id == work_schedule_subquery.c.doctor_id)
            )

            if condition is not None:
                query = query.where(condition)

            if min_avg_rating is not None:
                query = query.where(subquery.c.avg_rating >= min_avg_rating)

            if min_rating_count is not None:
                query = query.where(
                    subquery.c.rating_count >= min_rating_count)

            # Handle sorting
            if order_by and "avg_rating" in order_by:
                direction = desc if order_by["avg_rating"].lower(
                ) == "desc" else asc
                query = query.order_by(direction(subquery.c.avg_rating))
            else:
                # Default sorting by avg_rating desc
                query = query.order_by(desc(subquery.c.avg_rating))

            other_order_expressions = process_orderby(
                self.model_class, {k: v for k, v in (order_by or {}).items() if k != "avg_rating"})
            if other_order_expressions:
                query = query.order_by(*other_order_expressions)

            query = query.offset(skip).limit(limit)

            result = await self.session.execute(query)
            doctors = result.all()
            return [
                {
                    **doctor[0].as_dict,
                    'avg_rating': doctor[1],
                    'rating_count': doctor[2],
                    'latest_examination_price': {
                        'id': doctor[3],
                        'online_price': doctor[5],
                        'offline_price': doctor[6],
                        'created_at': doctor[7]
                    } if doctor[3] else None,
                    'work_schedules': doctor[8] if doctor[8] else []
                }
                for doctor in doctors
            ]
        except SQLAlchemyError as e:
            logging.error(f"Error in get_all: {e}")
            raise

    async def insert(self, data: dict[str, Any], *args: Any, **kwargs: Any) -> DoctorModel:
        try:
            await self._check_existing_user(data.get("phone_number", ""))
            await self._check_existing_doctor(data.get("email", ""), data.get("license_number", ""))

            user_model = self._create_user_model(data)
            doctor_model = self._create_doctor_model(data, user_model)

            self.session.add(doctor_model)
            await self.session.flush()  # This will assign an ID to the doctor_model

            # Create and add the examination price
            examination_price = self._create_examination_price(
                data, doctor_model.id)
            self.session.add(examination_price)

            await self.session.commit()
            return doctor_model
        except BadRequest as e:
            logging.error(f"BadRequest error in insert: {e}")
            await self.session.rollback()
            raise
        except SQLAlchemyError as e:
            logging.error(f"SQLAlchemy error in insert: {e}")
            await self.session.rollback()
            raise BadRequest(error_code=ErrorCode.SERVER_ERROR.name,
                             msg="Failed to register doctor: Database error")
        except Exception as e:
            logging.error(f"Unexpected error in insert: {e}")
            await self.session.rollback()
            raise BadRequest(error_code=ErrorCode.SERVER_ERROR.name,
                             msg="Failed to register doctor: Unexpected error")

    async def _check_existing_user(self, phone_number: str) -> None:
        user_exists = await self.session.scalar(
            select(exists().where(UserModel.phone_number == phone_number))
        )
        if user_exists:
            raise BadRequest(msg="User has already been registered",
                             error_code=ErrorCode.USER_HAVE_BEEN_REGISTERED.name)

    async def _check_existing_doctor(self, email: str, license_number: str) -> None:
        doctor_exists = await self.session.scalar(
            select(exists().where((DoctorModel.email == email) |
                   (DoctorModel.license_number == license_number)))
        )
        if doctor_exists:
            raise BadRequest(msg="Doctor with this email or license number has already been registered",
                             error_code=ErrorCode.EMAIL_OR_LICENSE_NUMBER_HAVE_BEEN_REGISTERED.name)

    def _create_user_model(self, data: dict[str, Any]) -> UserModel:
        return UserModel(
            phone_number=data.get("phone_number", ""),
            password_hash=PasswordHandler.hash(data.get("password_hash", "")),
            role=Role.DOCTOR.value
        )

    def _create_doctor_model(self, data: dict[str, Any], user_model: UserModel) -> DoctorModel:
        valid_fields = {field.name for field in DoctorModel.__table__.columns}
        filtered_doctor_data = {k: v for k,
                                v in data.items() if k in valid_fields}

        # if "online_price" in data and "offline_price" not in data:
        #     filtered_doctor_data["type_of_disease"] = TypeOfDisease.ONLINE.value
        # elif "offline_price" in data and "online_price" not in data:
        #     filtered_doctor_data["type_of_disease"] = TypeOfDisease.OFFLINE.value
        # elif "online_price" in data and "offline_price" in data:
        #     filtered_doctor_data["type_of_disease"] = TypeOfDisease.BOTH.value

        return DoctorModel(**filtered_doctor_data, user=user_model)

    def _create_examination_price(self, data: dict[str, Any], doctor_id: int) -> DoctorExaminationPriceModel:
        return DoctorExaminationPriceModel(
            doctor_id=doctor_id,
            offline_price=data.get("offline_price", 0.0),
            online_price=data.get("online_price", 0.0),
            is_active=True
        )

    async def count_record(self, where: Optional[Dict[str, Any]] = None):
        try:
            where_condition = destruct_where(self.model_class, where or {})
            query = select(self.model_class)
            if where_condition is not None:
                query = query.where(where_condition)
            return await self._count(query)
        except SQLAlchemyError as e:
            logging.error(f"Error in count_record: {e}")
            raise

    async def get_doctor_with_ratings(self, doctor_id: int) -> Optional[Dict[str, Any]]:
        try:
            query = (
                select(
                    self.model_class,
                    func.avg(RatingModel.rating).label('avg_rating'),
                    func.array_agg(RatingModel.comment).label('comments'),
                    DoctorExaminationPriceModel
                )
                .outerjoin(RatingModel)
                .outerjoin(DoctorExaminationPriceModel)
                .where(and_(
                    self.model_class.id == doctor_id,
                    self.model_class.verify_status != 0
                ))
                .group_by(self.model_class.id, DoctorExaminationPriceModel.id)
                .order_by(desc(DoctorExaminationPriceModel.created_at))
                .limit(1)
            )

            result: Result[Tuple[DoctorModel, Any, Any, DoctorExaminationPriceModel]] = await self.session.execute(query)
            row: Row[Tuple[DoctorModel, Any, Any,
                           DoctorExaminationPriceModel]] | None = result.first()

            if row is None:
                return None

            doctor, avg_rating, comments, latest_price = row
            doctor_dict = doctor.as_dict
            doctor_dict['avg_rating'] = float(
                avg_rating) if avg_rating is not None else 0
            doctor_dict['comments'] = [
                comment for comment in comments if comment is not None]

            if latest_price:
                doctor_dict['latest_examination_price'] = {
                    'offline_price': latest_price.offline_price,
                    'online_price': latest_price.online_price,
                    'is_active': latest_price.is_active,
                    'created_at': latest_price.created_at
                }
            else:
                doctor_dict['latest_examination_price'] = None

            return doctor_dict
        except SQLAlchemyError as e:
            logging.error(f"Error in get_doctor_with_ratings: {e}")
            raise

    async def add_workingschedule(self, doctor_id: int, data: RequestDoctorWorkScheduleNextWeek) -> Dict[str, Any]:
        try:
            # check have permit create te working
            doctor_check = select(DoctorModel).where(
                DoctorModel.id == doctor_id)

            data_check = await self.session.execute(doctor_check)
            data_check_model = data_check.scalar_one_or_none()

            if data_check_model is None:
                await self.session.rollback()
                raise BadRequest(
                    error_code=ErrorCode.DOCTOR_NOT_FOUND.name, errors={
                        "message": "doctor not found"
                    })
            if data_check_model.verify_status != 2:
                raise BadRequest(
                    error_code=ErrorCode.DOCTOR_NOT_FOUND.name, errors={
                        "message": "doctor is not verify, pls varyfi and try again"
                    })
            if data_check_model.type_of_disease != "both":
                if data_check_model.type_of_disease != data.examination_type:
                    await self.session.rollback()
                    raise BadRequest(
                        error_code=ErrorCode.FORBIDDEN.name, errors={
                            "message": f"You can't create working schedule for this {data.examination_type}"
                        })
            new_schedules = []
            conflicts = []
            for daily_schedule in data.work_schedule:
                for time_slot in daily_schedule.time_slots:
                    existing_schedules = await self.session.execute(
                        select(WorkScheduleModel).where(
                            and_(
                                WorkScheduleModel.doctor_id == doctor_id,
                                WorkScheduleModel.work_date == daily_schedule.work_date,
                                WorkScheduleModel.examination_type == data.examination_type
                            )
                        )
                    )
                    existing_schedules = existing_schedules.scalars().all()

                    for existing_schedule in existing_schedules:
                        await self.session.delete(existing_schedule)

                    query_doctor_model = select(DoctorModel).where(
                        DoctorModel.id == doctor_id).options(joinedload(DoctorModel.examination_prices))
                    doctor_model = await self.session.execute(query_doctor_model)
                    doctor_model = doctor_model.unique().scalar_one_or_none()
                    if doctor_model is None:
                        await self.session.rollback()
                        raise BadRequest(
                            error_code=ErrorCode.DOCTOR_NOT_FOUND.name, msg="Doctor not found")
                    new_schedule = WorkScheduleModel(
                        doctor_id=doctor_id,
                        work_date=daily_schedule.work_date,
                        start_time=time_slot.start_time,
                        end_time=time_slot.end_time,
                        examination_type=data.examination_type,
                        doctor=doctor_model
                    )
                    new_schedules.append(new_schedule)

            conflicts = await self._check_schedule_conflicts(doctor_id, new_schedules)

            if conflicts:
                await self.session.rollback()
                raise BadRequest(error_code=ErrorCode.SCHEDULE_CONFLICT.name, errors={
                    "message": "Conflicts detected with different examination types",
                    "conflicts": conflicts
                })

            self.session.add_all(new_schedules)
            await self.session.commit()
            return {"message": "Work schedule updated successfully"}

        except (BadRequest, Forbidden) as e:
            logging.error(f"Error in add_workingschedule: {e}")
            raise e
        except SQLAlchemyError as e:
            logging.error(f"Error in add_workingschedule: {e}")
            await self.session.rollback()
            raise BadRequest(msg="Failed to update work schedule",
                             error_code=ErrorCode.SERVER_ERROR.name,
                             errors={"message": f"Error in add_workingschedule: {e}"}) from e
        except Exception as e:
            logging.error(f"Error in add_workingschedule: {e}")
            await self.session.rollback()
            raise BadRequest(msg="Failed to update work schedule",
                             error_code=ErrorCode.SERVER_ERROR.name) from e

    async def _check_schedule_conflicts(self, doctor_id: int, new_schedules: List[WorkScheduleModel]) -> List[Dict[str, Any]]:
        conflicts = []
        for schedule in new_schedules:
            query = (
                select(WorkScheduleModel)
                .where(
                    and_(
                        WorkScheduleModel.doctor_id == doctor_id,
                        WorkScheduleModel.work_date == schedule.work_date,
                        WorkScheduleModel.examination_type != schedule.examination_type,
                        or_(
                            and_(
                                WorkScheduleModel.start_time <= schedule.start_time,
                                WorkScheduleModel.end_time > schedule.start_time
                            ),
                            and_(
                                WorkScheduleModel.start_time < schedule.end_time,
                                WorkScheduleModel.end_time >= schedule.end_time
                            )
                        )
                    )
                )
            )
            result = await self.session.execute(query)
            conflicting_schedules = result.scalars().all()
            if conflicting_schedules:
                conflicts.extend([
                    {
                        "work_date": cs.work_date.isoformat(),
                        "start_time": cs.start_time.isoformat(),
                        "end_time": cs.end_time.isoformat(),
                        "examination_type": cs.examination_type
                    }
                    for cs in conflicting_schedules
                ])
        return conflicts

    async def get_working_schedules_by_id(self, *, id: int):

        try:
            query = select(WorkScheduleModel).where(
                WorkScheduleModel.id == id)

            result_query = await self.session.execute(query)
            work_schedule_model = result_query.scalar_one_or_none()
            if work_schedule_model is None:
                raise BadRequest(
                    error_code=ErrorCode.WORK_SCHEDULE_NOT_FOUND.name, errors={
                        "message": "Work schedule not found"
                    })
            return work_schedule_model.as_dict
        except BadRequest as e:
            logging.error(f"Error in get_working_schedules_by_id: {e}")
            raise e
        except SQLAlchemyError as e:
            logging.error(f"Error in get_working_schedules: {e}")
            raise
        except Exception as ex:
            logging.error(f"Error in get_working_schedules: {ex}")
            raise

    async def get_working_schedules(self, doctor_id: int | None, start_date: date | None, end_date: date | None, examination_type: Literal["online", "ofline"] | None, ordered: bool | None) -> List[Dict[str, Any]]:

        try:
            query = select(WorkScheduleModel)
            conditions = []
            key: List[str] = await redis_working.get_all_keys()
            if key:
                for k in key:
                    if k.isdigit():
                        conditions.append(WorkScheduleModel.id != int(k))
            if doctor_id is not None:
                conditions.append(WorkScheduleModel.doctor_id == doctor_id)
            if start_date is not None and end_date is not None:
                conditions.append(
                    WorkScheduleModel.work_date.between(start_date, end_date))
            if examination_type:
                conditions.append(
                    WorkScheduleModel.examination_type == examination_type)
            if ordered is not None:
                conditions.append(WorkScheduleModel.ordered == ordered)
            if conditions:
                query = query.where(and_(*conditions))

            query = query.order_by(
                WorkScheduleModel.work_date, WorkScheduleModel.start_time)

            result = await self.session.execute(query)
            schedules = result.scalars().all()
            return [
                schedule.as_dict
                for schedule in schedules
            ]
        except SQLAlchemyError as e:
            logging.error(f"Error in get_working_schedules: {e}")
            raise
        except Exception as ex:
            logging.error(f"Error in get_working_schedules: {ex}")
            raise

    async def update_one(self, model: DoctorModel, data: dict[str, Any]):
        try:
            for key, value in data.items():
                setattr(model, key, value)
            await self.session.commit()
            await self.session.refresh(model)
            return model
        except SQLAlchemyError as e:
            logging.error(f"Error in update: {e}")
            await self.session.rollback()
            raise

    async def get_working_schedules_v2(self, doctor_id: int, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        try:
            query = select(WorkScheduleModel).where(and_(
                WorkScheduleModel.doctor_id == doctor_id,
                WorkScheduleModel.work_date.between(start_date, end_date)
            ))
            query = query.order_by(
                WorkScheduleModel.work_date, WorkScheduleModel.start_time)
            result = await self.session.execute(query)
            schedules = result.scalars().all()

            return [
                {
                    "work_date": schedule.work_date,
                    "start_time": schedule.start_time,
                    "end_time": schedule.end_time,
                }
                for schedule in schedules
            ]
        except SQLAlchemyError as e:
            logging.error(f"Error in get_working_schedules_v2 : {e}")
            raise

    async def get_patient_by_doctor_id(
        self,
        doctor_id: int | None,
        current_page: int = 1,
        page_size: int = 10,
        appointment_status: str | None = None,
        status_order: tuple[str, ...] = ("approved", "processing", "completed")
    ):
        try:
            main_query = select(AppointmentModel).options(
                joinedload(AppointmentModel.medical_record)
            )
            if doctor_id:
                main_query = main_query.where(
                    AppointmentModel.doctor_id == doctor_id,
                )
            if appointment_status:
                main_query = main_query.where(
                    AppointmentModel.status == appointment_status
                )
            # process code here
            result_apointmant = await self.session.execute(main_query)
            appointment_model = result_apointmant.unique().scalars().all()
            data_response = []
            patients_by_id = defaultdict(list)
            for appointment in appointment_model:
                if appointment.medical_record is not None and appointment.medical_record.doctor_read_id != doctor_id:
                    continue
                patients_by_id[appointment.patient_id].append(appointment)
            for patient_id, appointments in patients_by_id.items():
                latest_appointment = max(
                    appointments, key=lambda a: a.created_at)
                item = {}
                appointment_dict = latest_appointment.as_dict
                if "id" in appointment_dict:
                    appointment_dict["appointment_id"] = appointment_dict.pop(
                        "id")
                item.update({"patient": latest_appointment.patient.as_dict})
                appointment_dict.pop("patient_id", {})

                if doctor_id is None:
                    item.update(
                        {"doctor": latest_appointment.doctor.as_dict})
                    appointment_dict.pop("doctor_id")

                item.update(**appointment_dict)

                data_response.append(item)

                # pending,approved,rejected,completed,processing
            len_data_object = len(data_response)
            status_priority = {status: index for index,
                               status in enumerate(status_order)}
            sorted_appointments = sorted(
                data_response,
                key=lambda a: (status_priority.get(
                    a['appointment_status'], float('inf')), -a['created_at'])
            )

            return {
                "items": sorted_appointments,
                "total_page": math.ceil(len_data_object / page_size),
                "current_page": current_page,
                "page_size": page_size
            }

        except SQLAlchemyError as e:
            logging.error(f"Error in get_patient_by_doctor_id: {e}")
            raise e
        except Exception as e:
            logging.error(f"Error in get_patient_by_doctor_id: {e}")
            raise e
    # async def statistical_doctor_for_admin(self):
    #     try:
    #         query = select(
    #             func.count(case(
    #                 (DoctorModel.verify_status != 0, 1),
    #                 else_=None
    #             )).label('amount_doctor'),
    #             func.count(case(
    #                 ((DoctorModel.type_of_disease == TypeOfDisease.ONLINE.value)
    #                  & (DoctorModel.verify_status != 0), 1),
    #                 else_=None
    #             )).label('amount_doctor_online'),
    #             func.count(case(
    #                 ((DoctorModel.type_of_disease == TypeOfDisease.OFFLINE.value)
    #                  & (DoctorModel.verify_status != 0), 1),
    #                 else_=None
    #             )).label('amount_doctor_offline'),
    #             func.count(case(
    #                 ((DoctorModel.type_of_disease == TypeOfDisease.BOTH.value)
    #                  & (DoctorModel.verify_status != 0), 1),
    #                 else_=None
    #             )).label('amount_doctor_both')
    #         )

    #         result = await self.session.execute(query)
    #         row = result.fetchone()

    #         return {
    #             "amount_doctor": row.amount_doctor,
    #             "amount_doctor_online": row.amount_doctor_online,
    #             "amount_doctor_offline": row.amount_doctor_offline,
    #             "amount_doctor_both": row.amount_doctor_both
    #         }
    #     except SQLAlchemyError as e:
    #         logging.error(f"Error in statistical_doctor_for_admin: {e}")
    #         raise
