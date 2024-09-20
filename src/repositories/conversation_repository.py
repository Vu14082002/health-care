import logging as log
from datetime import date, datetime

from sqlalchemy import (
    Result,
    Row,
    and_,
    asc,
    case,
    delete,
    desc,
    exists,
    func,
    or_,
    select,
    update,
)
from sqlalchemy.orm import joinedload

from src.core.database.postgresql import PostgresRepository
from src.core.exception import BadRequest, InternalServer
from src.enum import AppointmentModelStatus, ErrorCode
from src.models.conversation_model import ConversationModel
from src.repositories.global_helper_repository import redis_working


class ConversationRepoitory(PostgresRepository[ConversationModel]):
    pass
