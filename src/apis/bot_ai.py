import requests

from src.config import config
from src.core import HTTPEndpoint
from src.core.exception import BadRequest
from src.enum import ErrorCode
from src.schema.bot_service_schema import QuestionSchema


class BotServiceApi(HTTPEndpoint):
    async def get(self, query_params: QuestionSchema):
        try:
            response_data = requests.get(
                config.BOT_SERVICE_URL, params=query_params.model_dump()
            )
            if response_data.status_code == 200:
                return response_data.json()
        except Exception:
            raise BadRequest(
                error_code=ErrorCode.BAD_REQUEST.name,
                errors={
                    "message": "Hiên tại tính năng đang update, vui lòng thử lại sau"
                },
            )
