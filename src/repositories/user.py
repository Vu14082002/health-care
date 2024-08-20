import logging
from typing import Any, Dict

from sqlalchemy import select

from src.core.database.postgresql import PostgresRepository, Transactional
from src.models.patient import PatientModel
from src.models.user import UserModel
from src.repositories.global_func import destruct_where


class UserRepository(PostgresRepository[UserModel]):

    async def insert_user(self, data: dict[str, Any]):
        _user = await self.create(data)
        return _user

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
