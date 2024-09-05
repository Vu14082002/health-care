import logging
from datetime import date, datetime, time
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import (Result, Row, and_, asc, case, delete, desc, exists,
                        func, or_, select)
from sqlalchemy.exc import SQLAlchemyError

from src.core.database.postgresql import PostgresRepository
from src.core.exception import BadRequest
from src.core.security.password import PasswordHandler
from src.enum import ErrorCode
from src.models.doctor_model import (DoctorExaminationPriceModel, DoctorModel,
                                     TypeOfDisease)
from src.models.rating_model import RatingModel
from src.models.user_model import Role, UserModel
from src.models.work_schedule_model import WorkScheduleModel
from src.repositories.global_func import destruct_where, process_orderby
from src.schema.doctor_schema import RequestDoctorWorkScheduleNextWeek
from src.schema.register import RequestRegisterDoctorSchema


class DoctorRepository(PostgresRepository[DoctorModel]):

    async def get_all(self, skip: int = 0, limit: int = 10, join_: Optional[set[str]] = None,
                      where: Optional[Dict[str, Any]] = None, order_by: Optional[Dict[str, str]] = None,
                      min_avg_rating: Optional[float] = None, min_rating_count: Optional[int] = None) -> List[Dict[str, Any]]:
        try:
            condition = destruct_where(self.model_class, where or {})

            subquery = (
                select(
                    RatingModel.doctor_id,
                    func.avg(RatingModel.rating).label('avg_rating'),
                    func.count(RatingModel.id).label('rating_count')
                )
                .group_by(RatingModel.doctor_id)
                .subquery()
            )
            latest_price_subquery = (
                select(
                    DoctorExaminationPriceModel.id,
                    DoctorExaminationPriceModel.doctor_id,
                    DoctorExaminationPriceModel.online_price,
                    DoctorExaminationPriceModel.offline_price,
                    DoctorExaminationPriceModel.ot_price_fee,
                    DoctorExaminationPriceModel.created_at,
                )
                .distinct(DoctorExaminationPriceModel.doctor_id)
                .order_by(
                    DoctorExaminationPriceModel.doctor_id,
                    desc(DoctorExaminationPriceModel.created_at)
                )
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
                    latest_price_subquery
                )
                .outerjoin(subquery, self.model_class.id == subquery.c.doctor_id)
                .outerjoin(latest_price_subquery, self.model_class.id == latest_price_subquery.c.doctor_id)
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

            # Apply any other sorting criteria
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
                        'ot_price_fee': doctor[7],
                        'created_at': doctor[8]
                    } if doctor[3] else None
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

        if "online_price" in data and "offline_price" not in data:
            filtered_doctor_data["type_of_disease"] = TypeOfDisease.ONLINE.value
        elif "offline_price" in data and "online_price" not in data:
            filtered_doctor_data["type_of_disease"] = TypeOfDisease.OFFLINE.value
        elif "online_price" in data and "offline_price" in data:
            filtered_doctor_data["type_of_disease"] = TypeOfDisease.BOTH.value

        return DoctorModel(**filtered_doctor_data, user=user_model)

    def _create_examination_price(self, data: dict[str, Any], doctor_id: int) -> DoctorExaminationPriceModel:
        return DoctorExaminationPriceModel(
            doctor_id=doctor_id,
            offline_price=data.get("offline_price", 0.0),
            online_price=data.get("online_price", 0.0),
            ot_price_fee=data.get("ot_price_fee", 200.0),
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
                    'ot_price_fee': latest_price.ot_price_fee,
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
            new_schedules = []
            conflicts = []
            for daily_schedule in data.work_schedule:
                for time_slot in daily_schedule.time_slots:
                    existing_schedule = await self.session.execute(
                        select(WorkScheduleModel).where(
                            and_(
                                WorkScheduleModel.doctor_id == doctor_id,
                                WorkScheduleModel.work_date == daily_schedule.work_date,
                                or_(
                                    and_(
                                        WorkScheduleModel.start_time <= time_slot.start_time,
                                        WorkScheduleModel.end_time > time_slot.start_time
                                    ),
                                    and_(
                                        WorkScheduleModel.start_time < time_slot.end_time,
                                        WorkScheduleModel.end_time >= time_slot.end_time
                                    )
                                )
                            )
                        )
                    )
                    if existing_schedule.scalar_one_or_none():
                        conflicts.append({
                            "date": daily_schedule.work_date.isoformat(),
                            "start_time": time_slot.start_time.isoformat(),
                            "end_time": time_slot.end_time.isoformat()
                        })
                    else:
                        new_schedule = WorkScheduleModel(
                            doctor_id=doctor_id,
                            work_date=daily_schedule.work_date,
                            start_time=time_slot.start_time,
                            end_time=time_slot.end_time,
                            examination_type=data.examination_type
                        )
                        new_schedules.append(new_schedule)

            if conflicts:
                await self.session.rollback()
                return {"message": "Conflicts detected", "conflicts": conflicts}

            self.session.add_all(new_schedules)
            _ = await self.session.commit()
            return {"message": "Work schedule updated successfully"}
        except SQLAlchemyError as e:
            logging.error(f"Error in add_workingschedule: {e}")
            await self.session.rollback()
            raise BadRequest(msg="Failed to update work schedule",
                             error_code=ErrorCode.SERVER_ERROR.name, errors={"message": f"Error in add_workingschedule: {e}"}) from e
        except Exception as e:
            logging.error(f"Error in add_workingschedule: {e}")
            await self.session.rollback()
            raise BadRequest(msg="Failed to update work schedule",
                             error_code=ErrorCode.SERVER_ERROR.name) from e

    async def get_uncentered_time(self, doctor_id: int, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        try:
            query = (
                select(WorkScheduleModel)
                .where(
                    and_(
                        WorkScheduleModel.doctor_id == doctor_id,
                        WorkScheduleModel.work_date.between(
                            start_date, end_date),
                        WorkScheduleModel.ordered == False
                    )
                )
                .order_by(WorkScheduleModel.work_date, WorkScheduleModel.start_time)
            )
            result = await self.session.execute(query)
            schedules = result.scalars().all()

            return [
                {
                    "work_date": schedule.work_date.isoformat(),
                    "start_time": schedule.start_time.isoformat(),
                    "end_time": schedule.end_time.isoformat(),
                    "examination_type": schedule.examination_type
                }
                for schedule in schedules
            ]
        except SQLAlchemyError as e:
            logging.error(f"Error in get_uncentered_time: {e}")
            raise

    async def get_working_schedules(self, doctor_id: int, start_date: date, end_date: date, examination_type: Optional[str] = None) -> List[Dict[str, Any]]:
        try:
            query = (
                select(WorkScheduleModel)
                .where(
                    and_(
                        WorkScheduleModel.doctor_id == doctor_id,
                        WorkScheduleModel.work_date.between(
                            start_date, end_date)
                    )
                )
                .order_by(WorkScheduleModel.work_date, WorkScheduleModel.start_time)
            )

            if examination_type:
                query = query.where(
                    WorkScheduleModel.examination_type == examination_type)

            result = await self.session.execute(query)
            schedules = result.scalars().all()

            return [
                {
                    "work_date": schedule.work_date,
                    "start_time": schedule.start_time,
                    "end_time": schedule.end_time,
                    "examination_type": schedule.examination_type
                }
                for schedule in schedules
            ]
        except SQLAlchemyError as e:
            logging.error(f"Error in get_working_schedules: {e}")
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

    async def get_available_slots(self, doctor_id: int, examination_type: TypeOfDisease, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        try:
            query = (
                select(WorkScheduleModel)
                .where(
                    and_(
                        WorkScheduleModel.doctor_id == doctor_id,
                        WorkScheduleModel.work_date.between(
                            start_date, end_date),
                        WorkScheduleModel.examination_type != examination_type
                    )
                )
                .order_by(WorkScheduleModel.work_date, WorkScheduleModel.start_time)
            )
            result = await self.session.execute(query)
            schedules = result.scalars().all()

            return [
                {
                    "work_date": schedule.work_date,
                    "start_time": schedule.start_time,
                    "end_time": schedule.end_time,
                    "examination_type": schedule.examination_type
                }
                for schedule in schedules
            ]
        except SQLAlchemyError as e:
            logging.error(f"Error in get_available_slots: {e}")
            raise

    async def update_work_schedule(self, doctor_id: int, examination_type: TypeOfDisease, schedules: List[Dict[str, Any]]) -> Dict[str, str]:
        try:
            # Delete existing schedules for the given examination type
            await self.session.execute(
                delete(WorkScheduleModel).where(
                    and_(
                        WorkScheduleModel.doctor_id == doctor_id,
                        WorkScheduleModel.examination_type == examination_type
                    )
                )
            )

            # Create new schedules
            new_schedules = []
            for schedule in schedules:
                new_schedule = WorkScheduleModel(
                    doctor_id=doctor_id,
                    work_date=schedule['work_date'],
                    start_time=schedule['start_time'],
                    end_time=schedule['end_time'],
                    examination_type=examination_type
                )
                new_schedules.append(new_schedule)

            # Check for conflicts with existing schedules
            conflicts = await self._check_schedule_conflicts(doctor_id, new_schedules)
            if conflicts:
                raise BadRequest(msg="Schedule conflicts detected",
                                 error_code=ErrorCode.SCHEDULE_CONFLICT.name, errors={"message": "time working is conflicts ", "conflicts": conflicts})

            self.session.add_all(new_schedules)
            await self.session.commit()
            return {"message": "Work schedule updated successfully"}
        except BadRequest:
            await self.session.rollback()
            raise
        except SQLAlchemyError as e:
            logging.error(f"Error in update_work_schedule: {e}")
            await self.session.rollback()
            raise BadRequest(msg="Failed to update work schedule",
                             error_code=ErrorCode.SERVER_ERROR.name)

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
                        "work_date": cs.work_date,
                        "start_time": cs.start_time,
                        "end_time": cs.end_time,
                        "examination_type": cs.examination_type
                    }
                    for cs in conflicting_schedules
                ])
        return conflicts
