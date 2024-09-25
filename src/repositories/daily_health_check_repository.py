import logging
from src.core.database.postgresql import PostgresRepository
from src.core.exception import BadRequest, InternalServer
from src.enum import ErrorCode
from src.models.daily_health_check_model import DailyHealCheckModel
from src.models.patient_model import PatientModel
from src.schema.daily_health_check_schema import DailyHealthCheckSchema

from sqlalchemy import insert, select, exists


class DailyHealthCheckRepository(PostgresRepository[DailyHealCheckModel]):

    async def create_one(self, data_schema: DailyHealthCheckSchema):
        try:
            check_exist = select(
                exists().where(PatientModel.id == data_schema.patient_id)
            )
            result_check_exist = await self.session.execute(check_exist)
            is_patient_exist = result_check_exist.scalar()
            if not is_patient_exist:
                raise BadRequest(
                    error_code=ErrorCode.NOT_FOUND.name,
                    errors={"message": "Patient not found"},
                )
            insert_data = insert(DailyHealCheckModel).values(**data_schema.model_dump())
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
