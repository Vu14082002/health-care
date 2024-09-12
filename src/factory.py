from functools import partial

from src.core.database.postgresql import get_session
from src.helper import (AppointmentHelper, DoctorHelper, MedicalRecordsHelper,
                        PatientHelper, UserHelper)
from src.models import (AppointmentModel, DoctorModel, MedicalRecordModel,
                        PatientModel, UserModel)
from src.repositories import (AppointmentRepository, DoctorRepository,
                              MedicalRecordsRepository, PatientRepository,
                              UserRepository)


class Factory:

    # Repositories
    user_repository = partial(UserRepository, UserModel)
    patient_repository = partial(PatientRepository, PatientModel)
    doctor_repository = partial(DoctorRepository, DoctorModel)
    appointment_repository = partial(AppointmentRepository, AppointmentModel)
    medical_records_repository = partial(
        MedicalRecordsRepository, MedicalRecordModel)

    async def get_patient_helper(self) -> PatientHelper:
        async with get_session() as session:
            return PatientHelper(patient_repository=self.patient_repository(db_session=session))

    async def get_user_helper(self) -> UserHelper:
        async with get_session() as session:
            return UserHelper(user_repository=self.user_repository(db_session=session))

    async def get_doctor_helper(self) -> DoctorHelper:
        async with get_session() as session:
            return DoctorHelper(doctor_repository=self.doctor_repository(db_session=session))

    async def get_appointment_helper(self) -> AppointmentHelper:
        async with get_session() as session:
            return AppointmentHelper(appointment_repository=self.appointment_repository(db_session=session))

    async def get_medical_records_helper(self) -> MedicalRecordsHelper:
        async with get_session() as session:
            return MedicalRecordsHelper(medical_records_repository=self.medical_records_repository(db_session=session))
