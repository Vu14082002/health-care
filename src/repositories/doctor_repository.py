import logging
from typing import Any, Dict, List, Optional

from sqlalchemy import exists, select
from sqlalchemy.exc import SQLAlchemyError

from src.core.database.postgresql import PostgresRepository
from src.core.exception import BadRequest
from src.core.security.password import PasswordHandler
from src.enum import ErrorCode
from src.models.doctor_model import DoctorModel
from src.models.user_model import Role, UserModel
from src.repositories.global_func import destruct_where, process_orderby
from src.schema.register import RequestRegisterDoctorSchema


class DoctorRepository(PostgresRepository[DoctorModel]):

    async def get_all(self, skip: int = 0, limit: int = 10, join_: Optional[set[str]] = None,
                      where: Optional[Dict[str, Any]] = None, order_by: Optional[Dict[str, str]] = None) -> List[DoctorModel]:
        try:
            condition = destruct_where(self.model_class, where or {})
            order_expressions = process_orderby(
                self.model_class, order_by or {"created_at": "desc"})

            query = select(self.model_class)
            if condition is not None:
                query = query.where(condition)
            query = query.order_by(
                *order_expressions).offset(skip).limit(limit)

            result = await self.session.execute(query)
            return list(result.scalars().all())
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
