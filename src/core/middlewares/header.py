# -*- coding: utf-8 -*-
import jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from src.core import logger
from src.core.exception import Forbidden
from src.core.security.authentication import JsonWebToken


class HeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        """
        The `dispatch` function processes incoming requests,
        extracts user information, validates JWT tokens, and
        handles tracking and user login updates.

        :param request: The `request` parameter in the
        `dispatch` method is an object of type `Request`. It
        contains information about the incoming HTTP request,
        such as headers, client IP address, and user-agent
        :type request: Request
        :param call_next: The `call_next` parameter in the
        `dispatch` method is a reference to the next middleware
        or endpoint handler in the chain. When `dispatch` is
        called, it passes the `request` object to `call_next` to
        continue the processing of the request through the
        middleware stack or to the final
        :return: The `response` variable is being returned at
        the end of the `dispatch` function after calling the
        `call_next` function with the `request` parameter.
        """
        _headers = dict(request.headers)
        _client_ip = request.client.host
        _user_agent = _headers.get("user-agent", "Unknown")

        if "authorization" in _headers and "python" not in _user_agent:
            try:
                _jwt_auth = JsonWebToken()
                # _tracking_helper = await Factory().get_tracking_helper()
                # _user_helper = await Factory().get_transaction_helper()
                _user_id = await _jwt_auth.validate(request)
                _data = {
                    "user_id": _user_id,
                    "ip": _client_ip,
                    "user_agent": _user_agent,
                    "location": _headers.get("x-location", "unknown"),
                }
                logger.info(_data)
                # await _tracking_helper.handle_tracking(_data)
                # _user_helper.update_last_login(_user_id)

            except Forbidden:
                logger.error("Token expired or invalid")
            except jwt.InvalidTokenError:
                logger.error("Invalid token")
        response = await call_next(request)
        return response
