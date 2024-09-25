from src.repositories.daily_health_check_repository import DailyHealthCheckRepository
from src.schema.daily_health_check_schema import DailyHealthCheckSchema


class DailyHealthCheckHelper:

    def __init__(self, daily_detail_repository: DailyHealthCheckRepository) -> None:
        self.daily_detail_repository = daily_detail_repository

    async def create_daily_health_check(self, data_schema: DailyHealthCheckSchema):
        result = await self.daily_detail_repository.create_one(data_schema)
        return result
