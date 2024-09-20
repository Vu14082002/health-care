import logging
import math
from typing import Any, Dict

from sqlalchemy import and_, exists, insert, select, update
from sqlalchemy.orm import joinedload

from src.core.database.postgresql import PostgresRepository, Transactional
from src.core.exception import BadRequest, InternalServer
from src.core.security.password import PasswordHandler
from src.enum import ErrorCode, Role
from src.models.appointment_model import AppointmentModel, AppointmentModelStatus
from src.models.medical_records_model import MedicalRecordModel
from src.repositories.global_func import destruct_where, process_orderby
from src.schema.medical_records_schema import RequestCreateMedicalRecordsSchema


class MedicalRecordsRepository(PostgresRepository[MedicalRecordModel]):

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 10,
        join_: set[str] | None = None,
        where: dict[str, Any] = {},
        order_by: dict[str, Any] = {},
    ):
        try:
            where_condition = destruct_where(MedicalRecordModel, where)
            order_by_process = process_orderby(MedicalRecordModel, order_by)
            query = (
                select(MedicalRecordModel)
                .where(where_condition)
                .order_by(*order_by_process)
                .offset(skip)
                .limit(limit)
            )  # type: ignore
            result_select = await self.session.execute(query)

            result_select = result_select.scalars().all()

            total_page = math.ceil(len(result_select) / limit)
            items = []
            for item in result_select:
                dict_item = item.as_dict
                dict_item.update(
                    {
                        "doctor_create": {
                            "first_name": item.doctor_create.first_name,
                            "last_name": item.doctor_create.last_name,
                            "phone_number": item.doctor_create.phone_number,
                            "email": item.doctor_create.email,
                            "address": item.doctor_create.address,
                        }
                    }
                )
                if (
                    where.get("patient_id", None) is None
                    and where.get("doctor_read_id", None) is None
                ):
                    dict_item.update(
                        {
                            "doctor_read": {
                                "first_name": item.doctor_read.first_name,
                                "last_name": item.doctor_read.last_name,
                                "phone_number": item.doctor_read.phone_number,
                                "email": item.doctor_read.email,
                                "address": item.doctor_read.address,
                            }
                        }
                    )
                items.append(dict_item)

            return {
                "items": items,
                "current_page": skip,
                "page_size": limit,
                "total_page": total_page,
            }
        except Exception as e:
            logging.error(e)
            raise e

    async def create_medical_records(self, *, value: dict[str, Any]):
        try:
            query_medical_record = await self.session.execute(
                select(MedicalRecordModel).where(
                    MedicalRecordModel.appointment_id == value["appointment_id"]
                )
            )
            check_medical_record_exist = query_medical_record.scalar_one_or_none()
            if check_medical_record_exist:
                raise BadRequest(
                    msg="Medical record already exists",
                    error_code=ErrorCode.MEDICAL_RECORD_EXIST.name,
                    errors={"message": "The medical record already exists"},
                )
            appointment = await self.session.execute(
                select(AppointmentModel).where(
                    and_(
                        AppointmentModel.id == value["appointment_id"],
                        AppointmentModel.doctor_id == value["doctor_create_id"],
                    )
                )
            )
            appointment = appointment.scalar_one_or_none()
            if not appointment:
                raise BadRequest(
                    msg="Invalid appointment or doctor",
                    error_code=ErrorCode.INVALID_APPOINTMENT.name,
                    errors={
                        "message": "The doctor does not have an active appointment with this patient"
                    },
                )
            if appointment.appointment_status == AppointmentModelStatus.COMPLETED.value:
                raise BadRequest(
                    msg="Invalid appointment",
                    error_code=ErrorCode.INVALID_APPOINTMENT.name,
                    errors={
                        "message": "The appointment is  completed, you can't create a medical record for it"
                    },
                )
            if appointment.appointment_status != AppointmentModelStatus.APPROVED.value:
                raise BadRequest(
                    msg="Invalid appointment",
                    error_code=ErrorCode.INVALID_APPOINTMENT.name,
                    errors={
                        "message": "The appointment is not approved yet, you can't create a medical record for it"
                    },
                )
            # Check if the medical record already exists
            value.update({"patient_id": appointment.patient_id})
            medical_record = await self.session.execute(
                insert(MedicalRecordModel).values(value)
            )
            appointment.appointment_status = AppointmentModelStatus.COMPLETED.value
            await self.session.commit()
            return {
                "message": "Medical record created successfully",
                "data": medical_record.scalars().first(),
            }

        except (BadRequest, InternalServer) as e:
            logging.error(e)
            await self.session.rollback()
            raise e
        except Exception as e:
            await self.session.rollback()
            logging.error(e)
            raise InternalServer(
                msg="Internal server error",
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": "Server error, please try again later"},
            ) from e

    async def update_medical_records(self, *, value: dict[str, Any]):
        try:
            query_medical_record = select(MedicalRecordModel).where(
                MedicalRecordModel.id == value["id"],
            )
            result_medical_record = await self.session.execute(query_medical_record)
            medical_record = result_medical_record.scalar_one_or_none()
            if medical_record is None:
                raise BadRequest(
                    msg="Invalid medical record",
                    error_code=ErrorCode.INVALID_MEDICAL_RECORD.name,
                    errors={"message": "The medical record does not exist"},
                )
            if medical_record.doctor_create_id != value["doctor_create_id"]:
                raise BadRequest(
                    msg="Invalid doctor",
                    error_code=ErrorCode.INVALID_MEDICAL_RECORD.name,
                    errors={
                        "message": "You are not authorized to update this medical record, only the doctor who created it can update it"
                    },
                )
            update_query = (
                update(MedicalRecordModel)
                .where(MedicalRecordModel.id == value["id"])
                .values(value)
            )
            _ = await self.session.execute(update_query)
            await self.session.commit()
            return {
                "message": "medical record updated successfully",
            }

        except (BadRequest, InternalServer) as e:
            logging.error(e)
            await self.session.rollback()
            raise e
        except Exception as e:
            await self.session.rollback()
            logging.error(e)
            raise InternalServer(
                msg="Internal server error",
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": "Server error, please try again later"},
            ) from e

    async def get_medical_record_by_appointment_id(
        self, user_id: int, appointment_id: int, role: str
    ):
        try:
            query_data = (
                select(MedicalRecordModel).where(
                    MedicalRecordModel.appointment_id == appointment_id,
                )
                # .options(
                #     joinedload(MedicalRecordModel.doctor_create),
                #     joinedload(MedicalRecordModel.patient_id),
                # )
            )

            result_query = await self.session.execute(query_data)
            medical_record = result_query.scalar_one_or_none()
            if medical_record is None:
                raise BadRequest(
                    msg="Invalid medical record",
                    error_code=ErrorCode.INVALID_MEDICAL_RECORD.name,
                    errors={
                        "message": "The medical record does not exist, maybe appointment is not completed yet"
                    },
                )
            item = medical_record.as_dict
            if role in [Role.DOCTOR.name, Role.ADMIN.name]:
                item.update(
                    {
                        "patient_id": {
                            "first_name": medical_record.patient.first_name,
                            "last_name": medical_record.patient.last_name,
                            "phone_number": medical_record.patient.phone_number,
                            "email": medical_record.patient.email,
                            "address": medical_record.patient.address,
                        }
                    }
                )
            if role in [Role.PATIENT.name, Role.ADMIN.name]:
                item.update(
                    {
                        "doctor_create_id": {
                            "first_name": medical_record.doctor_create.first_name,
                            "last_name": medical_record.doctor_create.last_name,
                            "phone_number": medical_record.doctor_create.phone_number,
                            "email": medical_record.doctor_create.email,
                            "address": medical_record.doctor_create.address,
                        }
                    }
                )
            return item
        except BadRequest as e:
            logging.error(e)
            raise e
        except Exception as e:
            logging.error(e)
            raise InternalServer(
                msg="Internal server error",
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": "Server error, please try again later"},
            ) from e
