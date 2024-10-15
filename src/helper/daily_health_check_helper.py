from src.core.decorator.exception_decorator import catch_error_helper
from src.repositories.daily_health_check_repository import DailyHealthCheckRepository
from src.schema.daily_health_check_schema import (
    DailyHealthCheckSchema,
    RequestGetAllDailyHealthSchema,
)


class DailyHealthCheckHelper:

    def __init__(self, daily_detail_repository: DailyHealthCheckRepository) -> None:
        self.daily_detail_repository = daily_detail_repository

    @catch_error_helper(message=None)
    async def create_daily_health_check(self, data_schema: DailyHealthCheckSchema):
        result = await self.daily_detail_repository.create_one(data_schema)
        return result

    @catch_error_helper(message=None)
    async def get_all_daily_health_check(
        self, query_params: RequestGetAllDailyHealthSchema, doctor_id: int | None
    ):
        result = await self.daily_detail_repository.get_all_daily_health_check_by_role(
            query_params, doctor_id
        )
        return result
