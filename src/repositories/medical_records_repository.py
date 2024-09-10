
import logging
from typing import Any, Dict

from sqlalchemy import exists, insert, select

from src.core.database.postgresql import PostgresRepository, Transactional
from src.core.exception import BadRequest, InternalServer
from src.core.security.password import PasswordHandler
from src.enum import ErrorCode
from src.models.medical_records_model import MedicalRecordModel
from src.repositories.global_func import destruct_where


class MedicalRecordsRepository(PostgresRepository[MedicalRecordModel]):
    pass
