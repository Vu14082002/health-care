from starlette.requests import Request

from src.core import HTTPEndpoint


class HealthCheck(HTTPEndpoint):
    async def get(self, request: Request):
        """
        day la api check server is working

        Args:
            request (Request): _description_

        Returns:
            _type_: _description_
        """
        return {"status": "ok"}
