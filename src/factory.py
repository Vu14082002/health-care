from functools import partial

from src.core.database.postgresql import get_session
from src.helper import (
    AppointmentHelper,
    ConversationHelper,
    DailyHealthCheckHelper,
    DoctorHelper,
    MedicalRecordsHelper,
    MessageHelper,
    NotificationHelper,
    PatientHelper,
    PostHelper,
    UserHelper,
)
from src.models import (
    AppointmentModel,
    ConversationModel,
    DailyHealCheckModel,
    DoctorModel,
    MedicalRecordModel,
    MessageModel,
    NotificationModel,
    PatientModel,
    PostModel,
    UserModel,
)
from src.repositories import (
    AppointmentRepository,
    ConversationRepoitory,
    DailyHealthCheckRepository,
    DoctorRepository,
    MedicalRecordsRepository,
    MessageRepository,
    NotificationRepository,
    PatientRepository,
    PostRepository,
    UserRepository,
)


class Factory:

    # Repositories
    user_repository = partial(UserRepository, UserModel)
    patient_repository = partial(PatientRepository, PatientModel)
    doctor_repository = partial(DoctorRepository, DoctorModel)
    appointment_repository = partial(AppointmentRepository, AppointmentModel)
    medical_records_repository = partial(MedicalRecordsRepository, MedicalRecordModel)
    conversation_repository = partial(ConversationRepoitory, ConversationModel)
    message_repository = partial(MessageRepository, MessageModel)
    daily_health_check_repository = partial(
        DailyHealthCheckRepository, DailyHealCheckModel
    )
    post_repository = partial(PostRepository, PostModel)
    notification_repository = partial(NotificationRepository, NotificationModel)

    async def get_patient_helper(self) -> PatientHelper:
        async with get_session() as session:
            return PatientHelper(
                patient_repository=self.patient_repository(db_session=session)
            )

    async def get_user_helper(self) -> UserHelper:
        async with get_session() as session:
            return UserHelper(user_repository=self.user_repository(db_session=session))

    async def get_doctor_helper(self) -> DoctorHelper:
        async with get_session() as session:
            return DoctorHelper(
                doctor_repository=self.doctor_repository(db_session=session)
            )

    async def get_appointment_helper(self) -> AppointmentHelper:
        async with get_session() as session:
            return AppointmentHelper(
                appointment_repository=self.appointment_repository(db_session=session)
            )

    async def get_medical_records_helper(self) -> MedicalRecordsHelper:
        async with get_session() as session:
            return MedicalRecordsHelper(
                medical_records_repository=self.medical_records_repository(
                    db_session=session
                )
            )

    async def get_conversation_helper(self) -> ConversationHelper:
        async with get_session() as session:
            return ConversationHelper(
                conversation_repository=self.conversation_repository(db_session=session)
            )

    async def get_message_helper(self) -> MessageHelper:
        async with get_session() as session:
            return MessageHelper(
                message_repository=self.message_repository(db_session=session)
            )

    async def get_daily_health_check_helper(self) -> DailyHealthCheckHelper:
        async with get_session() as session:
            return DailyHealthCheckHelper(
                daily_detail_repository=self.daily_health_check_repository(
                    db_session=session
                )
            )

    async def get_post_helper(self) -> PostHelper:
        async with get_session() as session:
            return PostHelper(post_repository=self.post_repository(db_session=session))

    async def get_notification_helper(self) -> NotificationHelper:
        async with get_session() as session:
            return NotificationHelper(
                notification_repository=self.notification_repository(db_session=session)
            )
