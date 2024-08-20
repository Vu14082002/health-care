import datetime
import json
import traceback
import typing
from abc import ABC, abstractmethod

import jwt
from starlette.requests import Request

from src.config import config
from src.core.cache import Cache
from src.core.database.postgresql import PostgresRepository
from src.core.exception import Forbidden
from src.core.logger import logger
from src.enum import ErrorCode


class Authorization(ABC):

    def __init__(self) -> None:
        super().__init__()
        self.auth_data = None

    @abstractmethod
    def validate(self, request: Request, *arg, **kwargs) -> typing.Any:
        pass


class JsonWebToken(Authorization):
    def __init__(self, access_key, refresh_key, algorithm, check_expire=True, check_is_valid=True, *args, **kwargs) -> None:
        super(JsonWebToken, self).__init__(*args, **kwargs)
        self.access_key = access_key
        self.refresh_key = refresh_key
        self.algorithm = algorithm
        self.check_expire = check_expire
        self.check_is_valid = check_is_valid

    def create_token(self, payload_data, *arg, **kwargs):
        token = jwt.encode(payload={
            "payload": payload_data,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }, key=self.access_key, algorithm=self.algorithm)
        refresh_token = jwt.encode(payload={
            "payload": payload_data,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=10)
        }, key=self.refresh_key, algorithm=self.algorithm)
        return {
            "access_token": token,
            "refresh_token": refresh_token
        }

    async def validate(self, request: Request, *arg, **kwargs):
        super(JsonWebToken, self).validate(request, *arg, **kwargs)
        redis = request.state.redis
        _token = ""
        try:
            _authorization = request.headers.get('authorization')
            if not _authorization:
                raise
            _type, _token = _authorization.split()
            if _type.lower() != 'bearer':
                raise
            _decode = jwt.decode(_token, key=self.access_key,
                                 algorithms=[self.algorithm])
            _user_cache = await redis.command("get", f"{config.CACHE_KEY_AUTH}:access_token:{_token}")
            if not _user_cache and self.check_expire:
                raise
            _user_cache = json.loads(_user_cache)

            _payload = _decode.get("payload", {})
            _payload['access_token'] = _token
            _payload['role'] = _user_cache.get('role')
            return _payload
        except jwt.exceptions.ExpiredSignatureError:
            if not self.check_expire:
                _decode = jwt.decode(
                    _token, options={"verify_signature": False})
                _payload = _decode.get("payload", {})
                _payload['access_token'] = _token
                return _payload
            raise Forbidden(msg="Token is expired",
                            error_code=ErrorCode.TOKEN_EXPIRED.name)
        except Exception as e:
            logger.error(e)
            raise Forbidden(msg="Authen Fail",
                            error_code=ErrorCode.AUTHEN_FAIL.name)


class APIKeyAuthen(Authorization):

    def __init__(self) -> None:
        super().__init__()

    async def validate(self, request: Request, *arg, **kwargs):
        try:
            api_db = request.state._state.get("api_key")
            if api_db is None:
                logger.error("api db not set")
                raise
            api_key = request.headers.get('authorization')
            _data = await api_db.find_one({"api_key": api_key})
            if not _data:
                logger.error("===== error api_key =====")
                logger.error(api_key)
                logger.error(_data)
                raise Exception()
            return _data
        except:
            traceback.print_exc()
            raise Forbidden()
