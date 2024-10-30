from typing import Any, Dict

import jwt

from src.config import config
from src.core.cache.redis_backend import RedisBackend
from src.core.decorator.exception_decorator import catch_error_helper
from src.core.exception import Unauthorized
from src.core.security.authentication import JsonWebToken
from src.core.security.password import PasswordHandler
from src.enum import CACHE_ACCESS_TOKEN, CACHE_REFRESH_TOKEN, ErrorCode, Role
from src.models.user_model import UserModel
from src.repositories import UserRepository
from src.schema.register import RequestAdminRegisterSchema, RequestRegisterPatientSchema

redis = RedisBackend(config.REDIS_URL)


class UserHelper:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository
        self.jwt = JsonWebToken()

    @catch_error_helper(message=None)
    async def register_admin(self, data: RequestAdminRegisterSchema):
        return await self.user_repository.register_admin(data)

    @catch_error_helper(message=None)
    async def register_patient(self, data: RequestRegisterPatientSchema):
        return await self.user_repository.register_patient(data)

    @catch_error_helper(message=None)
    async def insert_user(self, user: Dict[str, Any]):
        return await self.user_repository.insert_user(user)

    @catch_error_helper(message=None)
    async def login(self, phone_number: str, password: str) -> Dict[str, Any]:
        user = await self._authenticate_user(phone_number, password)
        user_all = self._scalar_user(user)
        token = self._gen_token(user_all)
        await redis.set(token["access_token"], phone_number, CACHE_ACCESS_TOKEN)
        return {"token": token, "user": user_all}

    async def _authenticate_user(self, phone_number: str, password: str) -> UserModel:
        user = await self.user_repository.get_one({"phone_number": phone_number})
        if user is None:
            raise Unauthorized(
                error_code=ErrorCode.UNAUTHORIZED.name,
                errors={"message": ErrorCode.msg_error_login.value},
            )
        if user.is_deleted:
            raise Unauthorized(
                error_code=ErrorCode.UNAUTHORIZED.name,
                errors={"message": ErrorCode.msg_delete_account_before.value},
            )
        if not PasswordHandler.verify(user.password_hash, plain_password=password):
            raise Unauthorized(
                error_code=ErrorCode.UNAUTHORIZED.name,
                errors={"message": ErrorCode.msg_wrong_password.name},
            )
        return user

    # def _generate_token_for_role(self, user: UserModel) -> Dict[str, str]:
    #     self._scalar_user(user)
    #     return self._gen_token(payload)
    @catch_error_helper(message=None)
    async def update_profile(self, user_id: int, data: dict[str, Any]):
        return await self.user_repository.update_profile(user_id, data)

    def _scalar_user(self, user: UserModel) -> Dict[str, str]:
        role_name = user.role
        if role_name == Role.ADMIN.value:
            payload = {**user.staff.as_dict, "role": role_name}
        elif role_name == Role.DOCTOR.value:
            if "verify_status" in user.doctor.as_dict:
                verify_status = user.doctor.as_dict["verify_status"]
                if verify_status not in [1,2]:
                    raise Unauthorized(
                        error_code=ErrorCode.UNAUTHORIZED.name,
                        errors={"message": ErrorCode.msg_not_verify.value},
                    )
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
        _decode = jwt.decode(
            jwt=token, key=config.ACCESS_TOKEN, algorithms=[config.ALGORITHM]
        )
        payload = _decode.get("payload", {})
        phone_number = payload.get("phone_number")
        if phone_number:
            await redis.delete(phone_number)
        return {"message": "Logged out successfully"}

    @catch_error_helper(message=None)
    async def reset_pwd(
        self, user_id: int, phone_number: str, password: str, old_password: str
    ):
        password_hash = PasswordHandler.hash(password)
        return await self.user_repository.reset_pwd(
            user_id, password_hash, old_password
        )
