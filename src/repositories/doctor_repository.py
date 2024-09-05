import logging
from datetime import date, datetime, time
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import (Result, Row, and_, asc, case, delete, desc, exists,
                        func, select)
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
                    DoctorExaminationPriceModel.doctor_id,
                    DoctorExaminationPriceModel.offline_price,
                    DoctorExaminationPriceModel.online_price,
                    DoctorExaminationPriceModel.ot_price_fee,
                    DoctorExaminationPriceModel.is_active,
                    DoctorExaminationPriceModel.effective_date
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
                        'offline_price': doctor[3].offline_price,
                        'online_price': doctor[3].online_price,
                        'ot_price_fee': doctor[3].ot_price_fee,
                        'is_active': doctor[3].is_active,
                        'effective_date': doctor[3].effective_date
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
                .where(self.model_class.id == doctor_id)
                .group_by(self.model_class.id, DoctorExaminationPriceModel.id)
                .order_by(desc(DoctorExaminationPriceModel.effective_date))
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
                    'effective_date': latest_price.effective_date
                }
            else:
                doctor_dict['latest_examination_price'] = None

            return doctor_dict
        except SQLAlchemyError as e:
            logging.error(f"Error in get_doctor_with_ratings: {e}")
            raise

    async def add_workingschedule(self, doctor_id: int, data: RequestDoctorWorkScheduleNextWeek) -> Dict[str, str]:
        try:
            new_schedules = []
            for daily_schedule in data.work_schedule:
                await self.session.execute(
                    delete(WorkScheduleModel).where(
                        and_(
                            WorkScheduleModel.doctor_id == doctor_id,
                            WorkScheduleModel.work_date == daily_schedule.work_date
                        )
                    )
                )
                # Create new schedules
                for time_slot in daily_schedule.time_slots:
                    new_schedule = WorkScheduleModel(
                        doctor_id=doctor_id,
                        work_date=daily_schedule.work_date,
                        start_time=time_slot.start_time,
                        end_time=time_slot.end_time
                    )
                    new_schedules.append(new_schedule)

            self.session.add_all(new_schedules)
            await self.session.commit()
            return {"message": "Work schedule updated successfully"}
        except SQLAlchemyError as e:
            logging.error(f"Error in add_workingschedule: {e}")
            await self.session.rollback()
            raise BadRequest(msg="Failed to update work schedule",
                             error_code=ErrorCode.SERVER_ERROR.name) from e

    async def add_workingschedule(self, doctor_id: int, data: RequestDoctorWorkScheduleNextWeek) -> Dict[str, str]:
        try:
            new_schedules = []
            for daily_schedule in data.work_schedule:
                _ = await self.session.execute(
                    delete(WorkScheduleModel).where(
                        and_(
                            WorkScheduleModel.doctor_id == doctor_id,
                            WorkScheduleModel.work_date == daily_schedule.work_date
                        )
                    )
                )
                #  remove duplicate time slots
                unique_time_slots = []
                for time_slot in daily_schedule.time_slots:
                    if not any(
                        ts.start_time == time_slot.start_time and ts.end_time == time_slot.end_time
                        for ts in unique_time_slots
                    ):
                        unique_time_slots.append(time_slot)

                # create new schedules
                for time_slot in unique_time_slots:
                    new_schedule = WorkScheduleModel(
                        doctor_id=doctor_id,
                        work_date=daily_schedule.work_date,
                        start_time=time_slot.start_time,
                        end_time=time_slot.end_time
                    )
                    new_schedules.append(new_schedule)

            self.session.add_all(new_schedules)
            await self.session.commit()
            return {"message": "Work schedule updated successfully"}
        except SQLAlchemyError as e:
            logging.error(f"Error in add_workingschedule: {e}")
            await self.session.rollback()
            raise BadRequest(msg="Failed to update work schedule",
                             error_code=ErrorCode.SERVER_ERROR.name) from e

    async def update_one(self, model: DoctorModel, data: dict[str, Any]) -> Optional[DoctorModel]:
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
