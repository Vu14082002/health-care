import logging
import logging as log
from typing import Any, Dict

from sqlalchemy import exists, select

from src.core.database.postgresql import PostgresRepository, Transactional
from src.core.exception import BadRequest
from src.core.security.password import PasswordHandler
from src.enum import ErrorCode
from src.models.patient_model import PatientModel
from src.models.user import Role, UserModel
from src.repositories.global_func import destruct_where
from src.schema.register import RequestAdminRegisterSchema


class UserRepository(PostgresRepository[UserModel]):

    async def register_admin(self, data: RequestAdminRegisterSchema):
        try:
            where = destruct_where(UserModel, {
                "phone_number": data.phone_number})
            if where is None:
                raise BadRequest(
                    ErrorCode.INVALID_PARAMETER.name, msg="Invalid parameter")

            exists_query = select(exists().where(where))

            patient_exists = await self.session.scalar(exists_query)
            if patient_exists:
                raise BadRequest(msg="User have been registered",
                                 error_code=ErrorCode.USER_HAVE_BEEN_REGISTERED.name)
            password_hash = PasswordHandler.hash(data.password_hash)
            user_model = UserModel()
            user_model.phone_number = data.phone_number
            user_model.password_hash = password_hash
            user_model.role = Role.ADMIN.value
            self.session.add(user_model)
            _ = await self.session.commit()
            return user_model
        except Exception as e:
            log.error(e)
            raise e

    async def insert_user(self, data: dict[str, Any]):
        pass

    async def get_by_id(self, user_id: int) -> UserModel | None:

        return await self.get_by('id', user_id)

    async def get_one(self, where: Dict[str, Any]):
        try:
            conditions = destruct_where(self.model_class, where)
            query = select(self.model_class)
            if conditions is not None:
                query = query.where(conditions)
            result = await self.session.execute(query)
            user_model: UserModel | None = result.unique().scalars().first()
            return user_model
        except Exception as e:
            logging.error("ERROR")
            logging.info(e)
            raise e
