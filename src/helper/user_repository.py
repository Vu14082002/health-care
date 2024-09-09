from typing import Any, Dict

import jwt

from src.config import config
from src.core.cache.redis_backend import RedisBackend
from src.core.database.postgresql import Transactional
from src.core.exception import Unauthorized
from src.core.security.authentication import JsonWebToken
from src.core.security.password import PasswordHandler
from src.enum import CACHE_ACCESS_TOKEN, CACHE_REFRESH_TOKEN, ErrorCode, Role
from src.models.patient_model import PatientModel
from src.models.user_model import UserModel
from src.repositories import UserRepository
from src.schema.register import RequestAdminRegisterSchema, RequestLoginSchema

redis = RedisBackend(config.REDIS_URL)


class UserHelper:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository
        self.jwt = JsonWebToken()

    async def register_admin(self, data: RequestAdminRegisterSchema):
        return await self.user_repository.register_admin(data)

    async def insert_user(self, user: Dict[str, Any]):
        return await self.user_repository.insert_user(user)

    async def login(self, phone_number: str, password: str) -> Dict[str, Any]:
        user: UserModel = await self._authenticate_user(phone_number, password)
        user_all = self._scalar_user(user)
        token = self._gen_token(user_all)
        await redis.set(token["access_token"], phone_number, CACHE_ACCESS_TOKEN)
        return {"token": token, "user": user_all}

    async def _authenticate_user(self, phone_number: str, password: str) -> UserModel:
        user = await self.user_repository.get_one({"phone_number": phone_number})
        if user is None:
            raise Unauthorized(msg="Phone number is not registered",
                               error_code=ErrorCode.UNAUTHORIZED.name)
        if not PasswordHandler.verify(user.password_hash, plain_password=password):
            raise Unauthorized(msg="Password is incorrect",
                               error_code=ErrorCode.UNAUTHORIZED.name)
        return user

    # def _generate_token_for_role(self, user: UserModel) -> Dict[str, str]:
    #     self._scalar_user(user)
    #     return self._gen_token(payload)

    def _scalar_user(self, user: UserModel) -> Dict[str, str]:
        role_name = user.role
        if role_name == Role.ADMIN.value:
            payload = user.as_dict
        elif role_name == Role.DOCTOR.value:
            payload = {**user.doctor.as_dict, "role": role_name}
        elif role_name == Role.PATIENT.value:
            payload = {**user.patient.as_dict, "role": role_name}
        else:
            raise ValueError(f"Unsupported role: {role_name}")
        return payload

    def _gen_token(self, payload: dict[str, Any]) -> Dict[str, str]:
        access_token = self.jwt.create_token(payload, exp=CACHE_ACCESS_TOKEN)
        refresh_token = self.jwt.create_token(
            {"access_token": access_token.get("access_token", "")},
            {"exp": CACHE_REFRESH_TOKEN},
        )
        return {
            "access_token": access_token.get("access_token", ""),
            "refresh_token": refresh_token.get("access_token", ""),
        }

    async def logout(self, token: str, *args: Any, **kwargs: dict[str, Any]):
        _decode = jwt.decode(jwt=token, key=config.ACCESS_TOKEN,
                             algorithms=[config.ALGORITHM])
        payload = _decode.get("payload", {})
        phone_number = payload.get("phone_number")
        if phone_number:
            await redis.delete(phone_number)
        return {"message": "Logged out successfully"}
