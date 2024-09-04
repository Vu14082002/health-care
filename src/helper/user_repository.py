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
from src.models.user_model import Role, UserModel
from src.repositories import UserRepository
from src.schema.register import RequestAdminRegisterSchema, RequestLoginSchema

redis = RedisBackend()


class UserHelper:

    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository
        self.jwt = JsonWebToken()

    async def register_admin(self, data: RequestAdminRegisterSchema):
        return await self.user_repository.register_admin(data)

    async def insert_user(self, user: Dict[str, Any]):
        return await self.user_repository.insert_user(user)

    async def login(self, phone_number: str, password: str) -> Dict[str, Any]:
        _user: UserModel | None = await self.user_repository.get_one({"phone_number": phone_number})
        if _user is None:
            raise Unauthorized(msg="Phone number is not registered",
                               error_code=ErrorCode.UNAUTHORIZED.name)
        if not PasswordHandler.verify(_user.password_hash, plain_password=password):
            raise Unauthorized(msg="Password is incorrect",
                               error_code=ErrorCode.UNAUTHORIZED.name)
        role_name = _user.role

        token = None
        if role_name == Role.ADMIN.value:
            token = self._gen_token(_user.as_dict)
        if role_name == Role.DOCTOR.value:
            data_token = _user.doctor.as_dict
            data_token["role"] = role_name
            token = self._gen_token(_user.doctor.as_dict)  # type:ignore
        if role_name == Role.PATIENT.value:
            patient = _user.patient
            data_token = patient.as_dict
            data_token["role"] = role_name
            token = self._gen_token(data_token)  # type:ignore
        await redis.set(token, phone_number, CACHE_ACCESS_TOKEN)
        return {"token": token}

    def _gen_token(self, payload: dict):
        access_token = self.jwt.create_token(payload, exp=CACHE_ACCESS_TOKEN)
        refresh_token = self.jwt.create_token(
            {"access_token": access_token.get("access_token", "")},
            {"exp": CACHE_REFRESH_TOKEN},
        )
        return {
            "access_token": access_token.get("access_token", ""),
            "refresh_token": refresh_token.get("access_token", ""),
        }
