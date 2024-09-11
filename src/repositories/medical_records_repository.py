import logging
from typing import Any, Dict

from sqlalchemy import and_, exists, insert, select

from src.core.database.postgresql import PostgresRepository, Transactional
from src.core.exception import BadRequest, InternalServer
from src.core.security.password import PasswordHandler
from src.enum import ErrorCode
from src.models.appointment_model import AppointmentModel
from src.models.medical_records_model import MedicalRecordModel
from src.repositories.global_func import destruct_where
from src.schema.medical_records_schema import RequestCreateMedicalRecordsSchema


class MedicalRecordsRepository(PostgresRepository[MedicalRecordModel]):

    async def create_medical_records(self, *, value: dict[str, Any]):
        try:
            appointment = await self.session.execute(
                select(AppointmentModel).where(
                    and_(
                        AppointmentModel.id == value["appointment_id"],
                        AppointmentModel.doctor_id == value["doctor_id"],
                    )
                )
            )
            appointment = appointment.scalar_one_or_none()
            if not appointment:
                raise BadRequest(msg="Invalid appointment or doctor",
                                 error_code=ErrorCode.INVALID_APPOINTMENT.name,
                                 errors={"message": "The doctor does not have an active appointment with this patient"})
            if appointment.appointment_status != "approved":
                raise BadRequest(msg="Invalid appointment",
                                 error_code=ErrorCode.INVALID_APPOINTMENT.name,
                                 errors={"message": "The appointment is not approved yet"})

            if appointment.appointment_status == "completed":
                raise BadRequest(msg="Invalid appointment",
                                 error_code=ErrorCode.INVALID_APPOINTMENT.name,
                                 errors={"message": "The appointment is already completed, you can't create a medical record for it"})
            # Check if the medical record already exists
            value.update({"patient_id": appointment.patient_id})
            medical_record = await self.session.execute(
                insert(MedicalRecordModel).values(value)
            )
            appointment.appointment_status = "completed"
            await self.session.commit()
            return {"message": "Medical record created successfully", "data": medical_record.scalars().first()}

        except (BadRequest, InternalServer) as e:
            logging.error(e)
            await self.session.rollback()
            raise e
        except Exception as e:
            await self.session.rollback()
            logging.error(e)
            raise InternalServer(msg="Internal server error",
                                 error_code=ErrorCode.SERVER_ERROR.name,
                                 errors={"message": "Server error, please try again later"}) from e
