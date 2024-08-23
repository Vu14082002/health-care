from typing import Any, Dict

from src.config import config
from src.core.cache.redis_backend import RedisBackend
from src.core.database.postgresql import Transactional
from src.core.exception import Unauthorized
from src.core.security.authentication import JsonWebToken
from src.core.security.password import PasswordHandler
from src.enum import (CACHE_ACCESS_TOKEN, CACHE_REFRESH_TOKEN,
                      KEY_CACHE_LOGOUT, ErrorCode)
from src.models.patient_model import PatientModel
from src.models.user import UserModel
from src.repositories import UserRepository
from src.schema.register import RequestAdminRegisterSchema, RequestLoginSchema
from src.schema.user import TokenSchema

redis = RedisBackend()


class UserHelper:

    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository
        self.jwt = JsonWebToken(config.ACCESS_TOKEN,
                                config.REFRESH_TOKEN, config.ALGORITHM)

    async def register_admin(self, data: RequestAdminRegisterSchema):
        return await self.user_repository.register_admin(data)

    async def insert_user(self, user: Dict[str, Any]):
        return await self.user_repository.insert_user(user)

    async def login(self, phone: str, password: str) -> Dict[str, Any]:
        _user: UserModel | None = await self.user_repository.get_one({"phone": phone})
        if _user is None:
            raise Unauthorized(msg="Phone number is not registered",
                               error_code=ErrorCode.UNAUTHORIZED.name)
        if not PasswordHandler.verify(_user.password, plain_password=password):
            raise Unauthorized(msg="Password is incorrect",
                               error_code=ErrorCode.UNAUTHORIZED.name)
        role_name = _user.roles[0].name

        _patient: PatientModel = _user.patient

        token: TokenSchema = TokenSchema(**_patient.as_dict)
        token.role = role_name
        token = self._gen_token(token.model_dump())  # type:ignore
        await redis.set(token, phone, CACHE_ACCESS_TOKEN)
        return {"token": token}

    def _gen_token(self, payload: dict) -> dict[str, str]:
        access_token = self.jwt.create_token(payload, exp=CACHE_ACCESS_TOKEN)
        refresh_token = self.jwt.create_token(
            {"access_token": access_token.get("access_token", "")},
            {"exp": CACHE_REFRESH_TOKEN},
        )
        return {
            "access_token": access_token.get("access_token", ""),
            "refresh_token": refresh_token.get("access_token", ""),
        }
