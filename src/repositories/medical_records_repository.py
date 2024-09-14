import logging
import math
from typing import Any, Dict

from sqlalchemy import and_, exists, insert, select

from src.core.database.postgresql import PostgresRepository, Transactional
from src.core.exception import BadRequest, InternalServer
from src.core.security.password import PasswordHandler
from src.enum import ErrorCode
from src.models.appointment_model import (AppointmentModel,
                                          AppointmentModelStatus)
from src.models.medical_records_model import MedicalRecordModel
from src.repositories.global_func import destruct_where, process_orderby
from src.schema.medical_records_schema import RequestCreateMedicalRecordsSchema


class MedicalRecordsRepository(PostgresRepository[MedicalRecordModel]):

    async def get_all(self, skip: int = 0, limit: int = 10, join_: set[str] | None = None, where: dict[str, Any] = {},
                      order_by:  dict[str, Any] = {}):
        try:
            where_condition = destruct_where(MedicalRecordModel, where)
            order_by_process = process_orderby(
                MedicalRecordModel, order_by)
            query = select(MedicalRecordModel).where(where_condition).order_by(
                *order_by_process).offset(skip).limit(limit)  # type: ignore
            result_select = await self.session.execute(query)

            result_select = result_select.scalars().all()

            total_page = math.ceil(len(result_select) / limit)

            return {
                "items": [item.as_dict for item in result_select],
                "current_page": skip,
                "page_size": limit,
                "total_page": total_page,
            }
        except Exception as e:
            logging.error(e)
            raise e

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
            if appointment.appointment_status != AppointmentModelStatus.APPROVED:
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
