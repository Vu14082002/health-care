# -*- coding: utf-8 -*-
from http.client import HTTPException
from starlette.requests import Request
from src.enum import ErrorCode
from src.lib.exception import Forbidden, Unauthorized
from abc import ABC, abstractmethod
from src.lib.logger import logger
from src.lib.postgres import PostgresClient
from src.lib.cache import Cache
from src.config import config
import datetime
import jwt
import traceback
import json


class Authorization(ABC):

    @abstractmethod
    def validate(self, request: Request, *arg, **kwargs):
        pass


class JsonWebToken(Authorization):
    def __init__(
        self,
        access_key,
        refresh_key,
        algorithm,
        check_expire=True,
        check_is_valid=True,
        *args,
        **kwargs,
    ) -> None:
        super(JsonWebToken, self).__init__(*args, **kwargs)
        self.access_key = access_key
        self.refresh_key = refresh_key
        self.algorithm = algorithm
        self.check_expire = check_expire
        self.check_is_valid = check_is_valid

    def create_token(self, payload_data, *arg, **kwargs):
        token = jwt.encode(
            payload={
                "payload": payload_data,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
            },
            key=self.access_key,
            algorithm=self.algorithm,
        )
        refresh_token = jwt.encode(
            payload={
                "payload": payload_data,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(days=10),
            },
            key=self.refresh_key,
            algorithm=self.algorithm,
        )
        return {"access_token": token, "refresh_token": refresh_token}

    async def validate(self, request: Request, *arg, **kwargs):
        super(JsonWebToken, self).validate(request, *arg, **kwargs)
        _token = ""
        try:
            _authorization = request.headers.get("authorization")
            if not _authorization:
                raise Unauthorized(msg="Authorization header missing")
            _type, _token = _authorization.split()
            if _type.lower() != "bearer":
                raise Unauthorized(msg="Invalid token type")

            _decode = jwt.decode(
                _token, key=self.access_key, algorithms=[self.algorithm]
            )

            _payload = _decode.get("payload", {})
            _payload["access_token"] = _token
            return _payload
        except jwt.ExpiredSignatureError:
            if not self.check_expire:
                _decode = jwt.decode(_token, options={"verify_signature": False})
                _payload = _decode.get("payload", {})
                _payload["access_token"] = _token
                return _payload
            raise Forbidden(msg="Token is expired")
        except Exception as e:
            logger.debug(e)
            raise Unauthorized(msg="Authentication failed")

class APIKeyAuthen(Authorization):

    def __init__(self) -> None:
        super().__init__()

    async def validate(self, request: Request, *arg, **kwargs):
        try:
            api_db = request.state._state.get("api_key")
            if api_db is None:
                logger.debug("api db not set")
                raise
            api_key = request.headers.get("authorization")
            _data = await api_db.find_one({"api_key": api_key})
            if not _data:
                logger.debug("===== error api_key =====")
                logger.debug(api_key)
                logger.debug(_data)
                raise Exception()
            return _data
        except:
            traceback.print_exc()
            raise Forbidden()
