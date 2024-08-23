# -*- coding: utf-8 -*-
import datetime
import typing
from abc import ABC, abstractmethod

import jwt
from starlette.requests import Request

from src.config import config
from src.core.cache.redis_backend import RedisBackend
from src.core.exception import Forbidden
from src.core.logger import logger
from src.enum import KEY_CACHE_LOGOUT, ErrorCode

redis = RedisBackend()


class Authorization(ABC):
    def __init__(self) -> None:
        """
        Initialize the object. This is called before __init__ is called to ensure that the object is ready to be used.


        @return A : class : ` pycassa. core. class_def. Base ` instance of
        """
        super().__init__()
        self.auth_data = None
        self.name = "base"

    @abstractmethod
    def validate(self, request: Request, *arg, **kwargs) -> typing.Any:
        """
        Validate the request. This is called by : meth : ` Request. __init__ ` and should return a boolean indicating whether or not the request is valid.

        @param request - The request to validate. This is passed by reference so it can be manipulated in a more convenient way.

        @return True if the request is valid False otherwise. Note that the return value is ignored for ` ` request ` `
        """
        pass


class JsonWebToken(Authorization):
    def __init__(self, *args, **kwargs) -> None:
        """
        Initialize the object with the config values. This is called by __init__ and should not be called directly.


        @return A : class : ` JsonWebToken ` object that can be used to authenticate with Bearer. You can use this as a constructor
        """
        super(JsonWebToken, self).__init__(*args, **kwargs)
        self.access_key = config.ACCESS_TOKEN
        self.refresh_key = config.ACCESS_TOKEN
        self.algorithm = config.ALGORITHM
        self.name = "bearerAuth"

    def create_token(self, payload_data, *arg, **kwargs):
        """
        Create a token for use with requests. This is a helper method to create a token that can be used to make requests to the API.

        @param payload_data - The payload data to send to the API.

        @return A dictionary containing the token and expiration time in seconds. Example :. { " access_token " : " my - token "
        """
        token = jwt.encode(
            payload={
                "payload": payload_data,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=60 * 5),
            },
            key=self.access_key,
            algorithm=self.algorithm,
        )
        return {
            "access_token": token,
        }

    async def _check_refesh_token_block(self, payload):
        """
        Check if the token is blocked. This is called by : meth : ` validate ` to check if the token is blocked.
        """
        if payload.get("access_token") is None:
            return
        _decode = jwt.decode(
            payload.get("access_token"),
            key=config.ACCESS_TOKEN,
            algorithms=[config.ALGORITHM],
        )
        username = _decode.get("payload")
        cache_block = await redis.get(
            f"{KEY_CACHE_LOGOUT}:{username.get('username')}:{payload.get('access_token')}"
        )
        if cache_block:
            raise Forbidden(
                msg="Token is blocked", error_code=ErrorCode.AUTHEN_FAIL.name
            )

    async def _check_access_token_block(self, payload, token):
        """
        Check if the token is blocked. This is called by : meth : ` validate ` to check if the token is blocked.
        """
        cache_block = await redis.get(
            f"{KEY_CACHE_LOGOUT}:{payload.get('username')}:{token}"
        )
        if cache_block:
            raise Forbidden(
                msg="Token is blocked", error_code=ErrorCode.AUTHEN_FAIL.name
            )

    async def validate(self, request: Request, *arg, **kwargs):
        """
        Validate token and return payload. This method is called by : meth : ` flask. RequestHandler. get ` to validate the token

        @param request - The request that triggered the validation

        @return The payload of the token or an empty dict if the token is not valid or expired. : 0.
        """
        super(JsonWebToken, self).validate(request, *arg, **kwargs)
        _token = ""
        try:
            _authorization = request.headers.get("authorization")
            # Raise an exception if the authorization is not authorized.
            if not _authorization:
                raise
            _type, _token = _authorization.split()

            # If the type isbearer raise an exception.
            if _type.lower() != "bearer":
                raise
            _decode = jwt.decode(
                _token, key=self.access_key, algorithms=[self.algorithm]
            )
            _payload = _decode.get("payload", {})
            await self._check_refesh_token_block(_payload)
            await self._check_access_token_block(_payload, _token)
            return _payload
        except jwt.exceptions.ExpiredSignatureError:
            raise Forbidden(
                msg="Token is expired", error_code=ErrorCode.TOKEN_EXPIRED.name
            )
        except Exception as e:
            logger.debug(e)
            raise Forbidden(msg="Authen Fail",
                            error_code=ErrorCode.AUTHEN_FAIL.name)
