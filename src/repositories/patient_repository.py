import logging
from typing import Any, Dict

from sqlalchemy import exists, insert, select

from src.core.database.postgresql import PostgresRepository, Transactional
from src.core.exception import BadRequest, InternalServer
from src.core.security.password import PasswordHandler
from src.enum import ErrorCode
from src.models import patient_model
from src.models.patient_model import PatientModel
from src.models.user_model import Role, UserModel
from src.repositories.global_func import destruct_where
from src.schema.register import RequestRegisterPatientSchema


class PatientRepository(PostgresRepository[PatientModel]):

    async def insert_patient(self, data: RequestRegisterPatientSchema) -> PatientModel:
        try:
            # Check if user exists by phone number
            user_exists = await self.session.scalar(
                select(exists().where(UserModel.phone_number == data.phone_number))
            )
            if user_exists:
                raise BadRequest(msg="User has already been registered",
                                 error_code=ErrorCode.USER_HAVE_BEEN_REGISTERED.name)

            # Check if patient exists by email
            patient_exists = await self.session.scalar(
                select(exists().where(PatientModel.email == data.email))
            )
            if patient_exists:
                raise BadRequest(msg="Patient with this email has already been registered",
                                 error_code=ErrorCode.USER_HAVE_BEEN_REGISTERED.name)

            # Create user and patient models
            password_hash = PasswordHandler.hash(data.password_hash)
            user_model = UserModel(
                phone_number=data.phone_number,
                password_hash=password_hash,
                role=Role.PATIENT.value
            )
            patient_data = data.model_dump(exclude={"password_hash"})
            patient_model = PatientModel(**patient_data, user=user_model)

            self.session.add(patient_model)
            await self.session.commit()
            return patient_model

        except BadRequest as e:
            raise e
        except Exception as e:
            logging.error(f"Failed to create patient: {e}")
            await self.session.rollback()
            raise InternalServer(msg="Failed to create patient",
                                 error_code=ErrorCode.SERVER_ERROR.name) from e

    async def get_by_id(self, patient_id: int):
        return await self.get_by('id', patient_id)
