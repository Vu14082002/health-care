import logging
from typing import Any, Dict

from sqlalchemy import exists, insert, select

from src.core.database.postgresql import PostgresRepository, Transactional
from src.core.exception import BadRequest, InternalServer
from src.core.security.password import PasswordHandler
from src.enum import ErrorCode
from src.models.appointment_model import AppointmentModel
from src.models.medical_records_model import MedicalRecordModel
from src.repositories.global_func import destruct_where
from src.schema.medical_records_schema import RequestCreateMedicalRecordsSchema


class MedicalRecordsRepository(PostgresRepository[MedicalRecordModel]):

    @Transactional()
    async def create_medical_records(self, *, value: RequestCreateMedicalRecordsSchema):
        try:
            # Check if the appointment exists and matches the doctor_id
            appointment = await self.session.execute(
                select(AppointmentModel).where(
                    AppointmentModel.id == value.appointment_id,
                    AppointmentModel.doctor_id == value.doctor_id
                )
            )
            appointment = appointment.scalar_one_or_none()

            if not appointment:
                raise BadRequest(msg="Invalid appointment or doctor",
                                 error_code=ErrorCode.INVALID_APPOINTMENT.name,
                                 errors={"message": "The appointment does not exist or does not match the provided doctor_id"})

            medical_record = await self.session.execute(
                insert(MedicalRecordModel).values(value.model_dump())
            )

            await self.session.commit()
            return medical_record.inserted_primary_key[0]

        except (BadRequest, InternalServer) as e:
            raise e
        except Exception as e:
            logging.error(e)
            raise InternalServer(msg="Internal server error",
                                 error_code=ErrorCode.SERVER_ERROR.name,
                                 errors={"message": "Server error, please try again later"}) from e
