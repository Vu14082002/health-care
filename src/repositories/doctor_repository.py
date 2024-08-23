import logging as log
from typing import Any, Dict, List, Optional, Sequence, Union

from numpy import where
from sqlalchemy import exists, insert, select

from src.core.database.postgresql import PostgresRepository, Transactional
from src.core.exception import BadRequest
from src.core.security.password import PasswordHandler
from src.enum import ErrorCode
from src.models.doctor_model import DoctorModel
from src.models.user import Role, UserModel
from src.repositories.global_func import destruct_where, process_orderby
from src.schema.register import RequestRegisterDoctorSchema


class DoctorRepository(PostgresRepository[DoctorModel]):

    async def get_all(self, skip: int = 0, limit: int = 10, join_: set[str] | None = None, where: Dict[str, Any] | None = None, order_by: Dict[str, str] | None = None) -> list[DoctorModel]:
        if where is None:
            where = {}
        if order_by is None:
            order_by = {"created_at": "desc"}
        try:
            condition: Any | None = destruct_where(
                self.model_class, where)
            order_expressions: List[Any] = process_orderby(
                self.model_class, order_by)
            query = select(self.model_class)
            if condition is not None:
                query = query.where(condition)
            query = query.order_by(
                *order_expressions).offset(skip).limit(limit)
            result = await self.session.execute(query)
            data: List[DoctorModel] = list(result.scalars().all())
            return data
        except Exception as e:
            log.error(e)
            raise e

    async def insert(self, data: RequestRegisterDoctorSchema):
        try:
            # check if user have been registered
            where = destruct_where(UserModel, {
                "phone_number": data.phone_number})
            if where is None:
                raise BadRequest(
                    error_code=ErrorCode.INVALID_PARAMETER.name, msg="Invalid parameter")

            exists_query = select(exists().where(where))

            patient_exists = await self.session.scalar(exists_query)
            if patient_exists:
                raise BadRequest(msg="User have been registered",
                                 error_code=ErrorCode.USER_HAVE_BEEN_REGISTERED.name)
            password_hash = PasswordHandler.hash(data.password_hash)
            user_model = UserModel()
            user_model.phone_number = data.phone_number
            user_model.password_hash = password_hash
            user_model.role = Role.DOCTOR.value
            doctor_model = data.model_dump(exclude={"password_hash"})
            docker_instance = DoctorModel(**doctor_model)
            docker_instance.user = user_model
            self.session.add(docker_instance)
            _ = await self.session.commit()
            return docker_instance
        except Exception as e:
            log.error(e)
            raise e

    async def count_record(self, where: dict[str, Any] | None = None):
        where_condition = destruct_where(
            self.model_class, where if where is not None else {})
        if where_condition is None:
            query = select(self.model_class)
        else:
            query = select(self.model_class).where(where_condition)
        return await super()._count(query)
