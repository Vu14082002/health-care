from functools import partial

from src.core.database.postgresql import get_session
from src.helper import PatientHelper, RoleHelper, UserHelper
from src.models import PatientModel, RoleModel, UserModel
from src.repositories import PatientRepository, RoleRepository, UserRepository


class Factory:

    # Repositories
    user_repository = partial(UserRepository, UserModel)
    role_repository = partial(RoleRepository, RoleModel)
    patient_repository = partial(PatientRepository, PatientModel)

    async def get_patient_helper(self) -> PatientHelper:
        async with get_session() as session:
            return PatientHelper(patient_repository=self.patient_repository(db_session=session))

    async def get_role_helper(self) -> RoleHelper:
        async with get_session() as session:
            return RoleHelper(role_repository=self.role_repository(db_session=session))

    async def get_user_helper(self) -> UserHelper:
        async with get_session() as session:
            return UserHelper(user_repository=self.user_repository(db_session=session))
