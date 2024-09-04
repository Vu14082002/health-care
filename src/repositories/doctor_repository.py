import logging
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import Result, Row, and_, case, exists, func, select, desc, asc
from sqlalchemy.exc import SQLAlchemyError

from src.core.database.postgresql import PostgresRepository
from src.core.exception import BadRequest
from src.core.security.password import PasswordHandler
from src.enum import ErrorCode
from src.models.doctor_model import DoctorModel
from src.models.rating_model import RatingModel
from src.models.user_model import Role, UserModel
from src.repositories.global_func import destruct_where, process_orderby
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
                    ).label('rating_count')
                )
                .outerjoin(subquery, self.model_class.id == subquery.c.doctor_id)
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
                {**doctor[0].as_dict, 'avg_rating': doctor[1],
                    'rating_count': doctor[2]}
                for doctor in doctors
            ]
        except SQLAlchemyError as e:
            logging.error(f"Error in get_all: {e}")
            raise

    async def insert(self, data: RequestRegisterDoctorSchema) -> DoctorModel:
        try:
            await self._check_existing_user(data.phone_number)
            await self._check_existing_doctor(data.email, data.license_number)

            user_model = self._create_user_model(data)
            doctor_model = self._create_doctor_model(data, user_model)

            self.session.add(doctor_model)
            await self.session.commit()
            return doctor_model
        except BadRequest:
            raise
        except Exception as e:
            logging.error(f"Error in insert: {e}")
            await self.session.rollback()
            raise BadRequest(error_code=ErrorCode.SERVER_ERROR.name,
                             msg="Failed to register doctor")

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

    def _create_user_model(self, data: RequestRegisterDoctorSchema) -> UserModel:
        return UserModel(
            phone_number=data.phone_number,
            password_hash=PasswordHandler.hash(data.password_hash),
            role=Role.DOCTOR.value
        )

    def _create_doctor_model(self, data: RequestRegisterDoctorSchema, user_model: UserModel) -> DoctorModel:
        doctor_data = data.model_dump(exclude={"password_hash"})
        return DoctorModel(**doctor_data, user=user_model)

    async def count_record(self, where: Optional[Dict[str, Any]] = None) -> int:
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
                    func.array_agg(RatingModel.comment).label('comments')
                )
                .outerjoin(RatingModel)
                .where(self.model_class.id == doctor_id)
                .group_by(self.model_class.id)
            )

            result: Result[Tuple[DoctorModel, Any, Any]] = await self.session.execute(query)
            row: Row[Tuple[DoctorModel, Any, Any]] | None = result.first()

            if row is None:
                return None

            doctor, avg_rating, comments = row
            doctor_dict = doctor.as_dict
            doctor_dict['avg_rating'] = float(
                avg_rating) if avg_rating is not None else 0
            doctor_dict['comments'] = [
                comment for comment in comments if comment is not None]

            return doctor_dict
        except SQLAlchemyError as e:
            logging.error(f"Error in get_doctor_with_ratings: {e}")
            raise
