import logging
from src.core.database.postgresql import PostgresRepository
from src.core.exception import BadRequest, InternalServer
from src.enum import ErrorCode
from src.models.appointment_model import AppointmentModel
from src.models.daily_health_check_model import DailyHealCheckModel
from src.models.patient_model import PatientModel
from src.schema.daily_health_check_schema import (
    DailyHealthCheckSchema,
    RequestGetAllDailyHealthSchema,
)

from sqlalchemy import func, insert, select, exists, update

from datetime import date


class DailyHealthCheckRepository(PostgresRepository[DailyHealCheckModel]):

    async def create_one(self, data_schema: DailyHealthCheckSchema):
        try:
            # check patient exist
            check_exist = select(
                exists().where(
                    AppointmentModel.patient_id == data_schema.patient_id,
                    AppointmentModel.id == data_schema.appointment_id,
                )
            )

            result_check_exist = await self.session.execute(check_exist)
            is_patient_exist = result_check_exist.scalar()
            if not is_patient_exist:
                raise BadRequest(
                    error_code=ErrorCode.NOT_FOUND.name,
                    errors={
                        "message": "apiointment not have with this patient, or patient is not owner by this appointment"
                    },
                )
            # check user have create in date if created will update
            date_check = date.today()
            if data_schema.date_create:
                date_check = data_schema.date_create

            query_daily_check = select(DailyHealCheckModel).where(
                DailyHealCheckModel.patient_id == data_schema.patient_id,
                DailyHealCheckModel.date_create == date_check,
            )
            result_daily_check = await self.session.execute(query_daily_check)
            data_result_daily_check = result_daily_check.scalars().all()
            data_len = len(data_result_daily_check)
            if data_len > 1:
                raise BadRequest(
                    error_code=ErrorCode.INVALID_REQUEST.name,
                    errors={
                        "message": "Duplicate daily health check, only one per day, maybe databse wrong dsata, pls delete then create again"
                    },
                )
            elif data_len == 1:
                # logic update
                update_data = (
                    update(DailyHealCheckModel)
                    .where(DailyHealCheckModel.id == data_result_daily_check[0].id)
                    .values(**data_schema.model_dump(exclude={"id"}))
                )
                _ = await self.session.execute(update_data)
                await self.session.commit()
                return {
                    "message": "Daily health check updated successfully",
                }
            else:
                # logic insert
                insert_data = insert(DailyHealCheckModel).values(
                    **data_schema.model_dump()
                )
                result_insert_data = await self.session.execute(insert_data)
                await self.session.commit()
                _ = result_insert_data.scalars().first()

                return {
                    "message": "Daily health check created successfully",
                }
        except (BadRequest, InternalServer) as e:
            await self.session.rollback()
            raise e
        except Exception as e:
            await self.session.rollback()
            logging.error(e)
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={
                    "message": "Server currently unable to handle this request,please try again later"
                },
            )

    async def get_all_daily_health_check_by_role(
        self, query_params: RequestGetAllDailyHealthSchema, doctor_id: int | None
    ):
        try:
            # check patient exist
            patient_query = select(PatientModel).where(
                PatientModel.id == query_params.patient_id
            )

            result_patient_query = await self.session.execute(patient_query)
            data_result_patient_query = result_patient_query.scalar_one_or_none()
            if not data_result_patient_query:
                raise BadRequest(
                    error_code=ErrorCode.NOT_FOUND.name,
                    errors={"message": "Patient not found"},
                )
            if doctor_id and data_result_patient_query.doctor_manage_id != doctor_id:
                raise BadRequest(
                    error_code=ErrorCode.UNAUTHORIZED.name,
                    errors={"message": "You are not permitted to acticate this patient"},
                )

            daily_query = select(DailyHealCheckModel).where(
                DailyHealCheckModel.patient_id == query_params.patient_id
            )
            if query_params.start_date:
                daily_query = daily_query.where(
                    DailyHealCheckModel.date_create >= query_params.start_date
                )
            if query_params.end_date:
                daily_query = daily_query.where(
                    DailyHealCheckModel.date_create <= query_params.end_date
                )
            total_count_query = select(func.count()).select_from(daily_query)

            # pagination
            daily_query = daily_query.offset(
                (query_params.current_page - 1) * query_params.page_size
            ).limit(query_params.page_size)
            result_daily_query = await self.session.execute(daily_query)
            data_result_patient_query = result_daily_query.scalars().all()
            # count total pages
            result_total_count_query = await self.session.execute(total_count_query)
            total_pages = (
                result_total_count_query.scalar_one() + query_params.page_size - 1
            ) // query_params.page_size
            return {
                "items": [item.as_dict for item in data_result_patient_query],
                "current_page": query_params.current_page,
                "page_size": query_params.page_size,
                "total_pages": total_pages,
            }
        except (BadRequest, InternalServer) as e:
            logging.error(e)
            raise e
        except Exception as e:
            logging.error(e)
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={
                    "message": "Server currently unable to handle this request,please try again later"
                },
            )
