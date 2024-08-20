from starlette.requests import Request

from src.core import HTTPEndpoint
from src.core.exception import BadRequest


class HealthCheck(HTTPEndpoint):
    async def get(self, request: Request):
        return {"status": "ok"}
