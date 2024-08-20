import jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from src.core import logger
from src.core.exception import Forbidden
from src.core.security.authentication import JsonWebToken
from src.factory import Factory


class HeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        _headers = dict(request.headers)

        if "authorization" in _headers:
            try:
                _jwt_auth = JsonWebToken()
                _user_helper = await Factory().get_admin_helper()

                _user_id = await _jwt_auth.validate(request)
                _user_helper.update_last_login(_user_id)

            except Forbidden:
                print("Token expired or invalid")
            except jwt.InvalidTokenError:
                print("Invalid token")

        response = await call_next(request)
        return response
