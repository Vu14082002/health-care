import logging
from typing import Any, Dict

from sqlalchemy import exists, insert, select

from src.core.database.postgresql import PostgresRepository, Transactional
from src.core.exception import BadRequest, InternalServer
from src.core.security.password import PasswordHandler
from src.enum import ErrorCode
from src.models import patient
from src.models.patient import PatientModel
from src.models.role import RoleModel
from src.models.user import UserModel
from src.models.user_roles import UserRolesModel
from src.repositories.global_func import destruct_where
from src.schema.register import RequestRegisterPatientSchema


class PatientRepository(PostgresRepository[PatientModel]):

    async def insert_patient(self, data: RequestRegisterPatientSchema) -> PatientModel:
        try:
            where = destruct_where(self.model_class, {
                "phone_number": data.phone_number})
            if where is None:
                raise BadRequest(
                    ErrorCode.INVALID_PARAMETER.name, msg="Invalid parameter")

            exists_query = select(exists().where(where))
            patient_exists = await self.session.scalar(exists_query)
            if patient_exists:
                raise BadRequest(msg="User have been registered",
                                 error_code=ErrorCode.USER_HAVE_BEEN_REGISTERED.name)

            # check email have been registered

            where = destruct_where(self.model_class, {"email": data.email})
            if where is not None:
                exists_query = select(exists().where(where))
                patient_exists = await self.session.scalar(exists_query)
                if patient_exists:
                    raise BadRequest(
                        error_code=ErrorCode.EMAIL_HAVE_BEEN_REGISTERED.name, msg="Email have been registered")

            # find role patient
            query = select(RoleModel).where(RoleModel.name == "patient")

            result_role = await self.session.execute(query)
            # role model process
            role_model: RoleModel | None = result_role.scalar_one_or_none()

            if role_model is None:
                raise InternalServer(
                    msg="Role patient not found", error_code=ErrorCode.SERVER_ERROR.name)

            # user_model process
            password_hash = PasswordHandler.hash(data.password)
            user_model = UserModel()
            user_model.phone = data.phone_number
            user_model.password = password_hash
            user_model.roles.append(role_model)

            # patient model process

            patient_data = data.model_dump(exclude={"password"})

            patient_model = PatientModel(**patient_data)
            patient_model.user = user_model

            self.session.add(patient_model)
            await self.session.commit()
            return patient_model
        except BadRequest as e:
            raise e
        except InternalServer as e:
            raise e
        except Exception as e:
            logging.error(f"Failed to create patient: {e}")
            await self.session.rollback()
            raise InternalServer(msg="Failed to create patient",
                                 error_code=ErrorCode.SERVER_ERROR.name) from e

    async def get_by_id(self, patient_id: int):
        return await self.get_by('id', patient_id)
