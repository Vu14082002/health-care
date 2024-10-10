import logging
import logging as log
from typing import Any, Dict

from sqlalchemy import and_, exists, select, update

from src.core.database.postgresql import PostgresRepository
from src.core.decorator.exception_decorator import exception_handler
from src.core.exception import BadRequest
from src.core.security.password import PasswordHandler
from src.enum import ErrorCode
from src.models.doctor_model import DoctorModel
from src.models.patient_model import PatientModel
from src.models.user_model import Role, UserModel
from src.repositories.global_func import destruct_where
from src.schema.register import RequestAdminRegisterSchema


class UserRepository(PostgresRepository[UserModel]):

    async def register_admin(self, data: RequestAdminRegisterSchema):
        try:
            where = destruct_where(UserModel, {"phone_number": data.phone_number})
            if where is None:
                raise BadRequest(
                    ErrorCode.INVALID_PARAMETER.name, msg="Invalid parameter"
                )

            exists_query = select(exists().where(where))

            patient_exists = await self.session.scalar(exists_query)
            if patient_exists:
                raise BadRequest(
                    msg="User have been registered",
                    error_code=ErrorCode.USER_HAVE_BEEN_REGISTERED.name,
                )
            password_hash = PasswordHandler.hash(data.password_hash)
            user_model = UserModel()
            user_model.phone_number = data.phone_number
            user_model.password_hash = password_hash
            user_model.role = Role.ADMIN.value
            self.session.add(user_model)
            _ = await self.session.commit()
            return user_model
        except Exception as e:
            log.error(e)
            raise e

    async def insert_user(self, data: dict[str, Any]):
        pass

    async def get_by_id(self, user_id: int):
        return await self.get_by("id", user_id)

    async def get_one(self, where: Dict[str, Any]):
        try:
            conditions = destruct_where(self.model_class, where)
            query = select(self.model_class)
            if conditions is not None:
                query = query.where(conditions)
            result = await self.session.execute(query)
            user_model: UserModel | None = result.unique().scalars().first()
            return user_model
        except Exception as e:
            logging.error("ERROR")
            logging.info(e)
            raise e

    @exception_handler
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
                        "message": "This phone number has been used by another user"
                    },
                )
        if value_check.get("email", None) is not None:
            is_email_exists = await self._is_email_exist(
                value_check.get("email"), user_id
            )
            if is_email_exists:
                raise BadRequest(
                    error_code=ErrorCode.INVALID_PARAMETER.name,
                    msg="You can't update email to an existing one",
                    errors={"message": "This email has been used by another user"},
                )

        if value_update:
            for key, value in value_update.items():
                setattr(model, key, value)

            await self.session.commit()
        return model.as_dict

    async def _is_phone_exist(self, phone_number: str, user_id: int):
        query_check_phone = select(
            exists().where(
                and_(
                    UserModel.phone_number == phone_number,
                    UserModel.id != user_id,
                )
            )
        )
        resukt_query_check_phone = await self.session.execute(query_check_phone)
        return resukt_query_check_phone.scalar_one()

    async def _is_email_exist(self, email: str, user_id: int):
        query_check_doctor_email = select(
            exists().where(
                and_(
                    DoctorModel.email == email,
                    DoctorModel.id != user_id,
                )
            )
        )
        resukt_query_check_doctor_email = await self.session.execute(
            query_check_doctor_email
        )

        is_doctor_email_exists = resukt_query_check_doctor_email.scalar_one()

        query_check_patient_email = select(
            exists().where(
                and_(
                    PatientModel.email == email,
                    PatientModel.id != user_id,
                )
            )
        )
        result_query_check_patient_email = await self.session.execute(
            query_check_patient_email
        )
        is_patient_email_exists = result_query_check_patient_email.scalar_one()

        return is_doctor_email_exists or is_patient_email_exists

    async def reset_pwd(self, user_id: int, password_hash: str):
        update_statement = (
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(password_hash=password_hash)
            .returning(UserModel)  # Return the ID (or another column)
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
