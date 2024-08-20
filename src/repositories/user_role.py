from sqlalchemy import select
from sqlalchemy.orm import joinedload
from src.core.database.postgresql import PostgresRepository, Transactional
from src.models import UserRoles
from src.core import logger
from typing import Any


class UserRoleRepository(PostgresRepository[UserRoles]):

    @Transactional()
    async def insert_user_role(self, data: dict[str, Any]):
        _user_role = await self.create(data)
        return _user_role
