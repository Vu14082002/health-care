from functools import partial

from src.core.database.postgresql import get_session
from src.helper import DoctorHelper, PatientHelper, UserHelper
from src.models import DoctorModel, PatientModel, UserModel
from src.repositories import (DoctorRepository, PatientRepository,
                              UserRepository, doctor_repository)


class Factory:

    # Repositories
    user_repository = partial(UserRepository, UserModel)
    patient_repository = partial(PatientRepository, PatientModel)
    doctor_repository = partial(DoctorRepository, DoctorModel)

    async def get_patient_helper(self) -> PatientHelper:
        async with get_session() as session:
            return PatientHelper(patient_repository=self.patient_repository(db_session=session))

    async def get_user_helper(self) -> UserHelper:
        async with get_session() as session:
            return UserHelper(user_repository=self.user_repository(db_session=session))

    async def get_doctor_helper(self) -> DoctorHelper:
        async with get_session() as session:
            return DoctorHelper(doctor_repository=self.doctor_repository(db_session=session))
