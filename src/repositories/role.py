from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.core import logger
from src.core.database.postgresql import PostgresRepository, Transactional
from src.models import RoleModel


class RoleRepository(PostgresRepository[RoleModel]):
    pass
