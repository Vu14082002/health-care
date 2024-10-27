import asyncio
import logging
from typing import Any, Dict, Optional

from sqlalchemy import and_, exists, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.postgresql import PostgresRepository
from src.core.database.postgresql.session import get_session
from src.core.decorator.exception_decorator import (
    catch_error_repository,
)
from src.core.exception import BadRequest, InternalServer
from src.core.security.password import PasswordHandler
from src.enum import ErrorCode
from src.models.doctor_model import DoctorModel
from src.models.patient_model import PatientModel
from src.models.staff_model import StaffModel
from src.models.user_model import Role, UserModel
from src.repositories.global_func import destruct_where
from src.schema.register import RequestAdminRegisterSchema, RequestRegisterPatientSchema


class UserRepository(PostgresRepository[UserModel]):

    @catch_error_repository(message=None)
    async def register_admin(self, data: RequestAdminRegisterSchema):

        is_phone_exists = await self._is_phone_exist(phone_number=data.phone_number)
        is_mail_exists = await self._is_email_exist(email=data.email)
        if is_phone_exists:
            raise BadRequest(
                error_code=ErrorCode.USER_HAVE_BEEN_REGISTERED.name,
                errors={
                    "message": ErrorCode.msg_phone_have_been_registered.value
                },
            )
        if is_mail_exists:
            raise BadRequest(
                error_code=ErrorCode.USER_HAVE_BEEN_REGISTERED.name,
                errors={"message": ErrorCode.msg_email_have_been_registered.value},
            )
        password_hash = PasswordHandler.hash(data.password_hash)
        user_model = UserModel()
        user_model.phone_number = data.phone_number
        user_model.password_hash = password_hash
        user_model.role = Role.ADMIN.value
        staff_model = StaffModel(**data.model_dump(exclude={"password_hash"}))
        user_model.staff = staff_model
        # add user and staff to session
        self.session.add(user_model)
        _ = await self.session.commit()
        return staff_model.as_dict

    @catch_error_repository(message=None)
    async def register_patient(self, data: RequestRegisterPatientSchema):
        is_phone_exists = await self._is_phone_exist(phone_number=data.phone_number)
        is_mail_exists = await self._is_email_exist(email=data.email)
        if is_phone_exists:
            raise BadRequest(
                error_code=ErrorCode.USER_HAVE_BEEN_REGISTERED.name,
                errors={
                    "message": ErrorCode.msg_phone_have_been_registered.value
                },
            )
        if is_mail_exists:
            raise BadRequest(
                error_code=ErrorCode.USER_HAVE_BEEN_REGISTERED.name,
                errors={"message": ErrorCode.msg_email_have_been_registered.value},
            )
        password_hash = PasswordHandler.hash(data.password_hash)
        user_model = UserModel(
            phone_number=data.phone_number,
            password_hash=password_hash,
            role=Role.PATIENT.value,
        )
        patient_model = PatientModel(**data.model_dump(exclude={"password_hash"}))
        user_model.patient = patient_model
        self.session.add(user_model)
        await self.session.commit()
        return patient_model.as_dict

    @catch_error_repository(message=None)
    async def get_by_id(self, user_id: int):
        return await self.get_by("id", user_id)

    @catch_error_repository(message=None)
    async def get_one(self, where: Dict[str, Any]):
        conditions = destruct_where(self.model_class, where)
        query = select(self.model_class)
        if conditions is not None:
            query = query.where(conditions)
        result = await self.session.execute(query)
        user_model: UserModel | None = result.unique().scalars().first()
        return user_model

    @catch_error_repository(message=None)
    async def update_profile(self, user_id: int, data: dict[str, Any]):
        user_model = await self.get_one({"id": user_id})
        if user_model is None:
            raise BadRequest(
                error_code=ErrorCode.NOT_FOUND.name,
                msg="User not found",
            )
        model: PatientModel | DoctorModel = (
            user_model.patient
            if user_model.role == Role.PATIENT.value
            else user_model.doctor
        )
        value_update = {
            k: v for k, v in data.items() if k in model.as_dict and v is not None
        }
        # check value_update phone_number or email exists
        value_check = {
            k: v for k, v in value_update.items() if k in ["phone_number", "email"]
        }

        if value_check.get("phone_number", None) is not None:
            is_phone_exists = await self._is_phone_exist(
                value_check.get("phone_number"), user_id
            )
            if is_phone_exists:
                raise BadRequest(
                    error_code=ErrorCode.INVALID_PARAMETER.name,
                    errors={
                        "message": ErrorCode.msg_phone_have_been_registered.value
                    },
                )
        if value_check.get("email", None) is not None:
            is_email_exists = await self._is_email_exist(
                value_check.get("email"), user_id
            )
            if is_email_exists:
                raise BadRequest(
                    error_code=ErrorCode.INVALID_PARAMETER.name,
                    errors={"message": ErrorCode.msg_email_have_been_registered.value},
                )
        if value_update:
            for key, value in value_update.items():
                setattr(model, key, value)
            await self.session.commit()
        return model.as_dict

    async def _is_phone_exist(
        self,
        phone_number: str,
        user_id: int | None = None,
        session: Optional[AsyncSession] = None,
    ):
        """
        this function is used to check if phone number is exist in database

        """
        _session = session or self.session
        user_filter = UserModel.phone_number == phone_number
        if user_id:
            user_filter = and_(user_filter, UserModel.id != user_id)
        query_check_phone = select(exists().where(user_filter))
        result_query_check_phone = await _session.execute(query_check_phone)
        return result_query_check_phone.scalar_one()

    async def _is_email_exist(
        self,
        email: str,
        user_id: int | None = None,
        session: Optional[AsyncSession] = None,
    ):
        _session = session or self.session
        doctor_filter = DoctorModel.email == email
        patient_filter = PatientModel.email == email
        staff_filter = StaffModel.email == email

        if user_id is not None:
            doctor_filter = and_(doctor_filter, DoctorModel.id != user_id)
            patient_filter = and_(patient_filter, PatientModel.id != user_id)
            staff_filter = and_(staff_filter, StaffModel.id != user_id)

        # Check email existence in doctor
        query_check_doctor_email = select(exists().where(doctor_filter))
        result_query_check_doctor_email = await _session.execute(
            query_check_doctor_email
        )
        is_doctor_email_exists = result_query_check_doctor_email.scalar_one()

        # Check email existence in patient
        query_check_patient_email = select(exists().where(patient_filter))
        result_patient_email = await _session.execute(query_check_patient_email)
        is_patient_email_exists = result_patient_email.scalar_one()

        # Check email existence in staff
        query_check_staff_email = select(exists().where(staff_filter))
        result_staff_email = await _session.execute(query_check_staff_email)
        is_staff_email_exists = result_staff_email.scalar_one()

        # Return True if the email exists in any of the models
        return (
            is_doctor_email_exists or is_patient_email_exists or is_staff_email_exists
        )

    @catch_error_repository(message=None)
    async def reset_pwd(self, user_id: int, password_hash: str, old_password: str):
        user_query = select(UserModel).where(UserModel.id == user_id)
        result_user_query = await self.session.execute(user_query)
        user = result_user_query.scalar_one_or_none()
        if not user:
            raise BadRequest(
                error_code=ErrorCode.NOT_FOUND.name,
                errors={"message": ErrorCode.msg_user_not_found.value},
            )
        if not PasswordHandler.verify(
            user.password_hash, plain_password=old_password
        ):
            raise BadRequest(
                error_code=ErrorCode.UNAUTHORIZED.name,
                errors={"message": ErrorCode.msg_incorrect_old_password.value},
            )
        update_statement = (
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(password_hash=password_hash)
            .returning(UserModel)
        )
        result_update_statement = await self.session.execute(update_statement)
        await self.session.commit()

        # Fetch the updated value
        data_update_statement = result_update_statement.scalars().first()
        if not data_update_statement:
            raise BadRequest(
                error_code=ErrorCode.NOT_FOUND.name,
                errors={"message": "Something went wrong when updating password"},
            )
        return data_update_statement.as_dict
