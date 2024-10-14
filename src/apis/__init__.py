from src.apis.appointment import AppointmentApi, AppointmentApiGET
from src.apis.auth import (
    AdminNotifyRegisterMail,
    AdminRegisterApi,
    DoctorForeignRegisterApi,
    DoctorForeignRejectApi,
    DoctorLocalRegisterApi,
    DoctorOtherVerifyApi,
    DoctorOtherVerifyApiPut,
    DoctorOtherVerifyFinalApiPut,
    LoginApi,
    LogoutApi,
    PatientRegisterApi,
)
from src.apis.bot_ai import BotServiceApi
from src.apis.conversation_api import ConversationApi
from src.apis.daily_health_check_api import DailyDealthCheckApi
from src.apis.docter_api import (
    DoctorGetPatientsApi,
    DoctorGetPatientsByIdApi,
    GetAllDoctorApi,
    GetAllDoctorForeignAPi,
    GetAllDoctorLocalAPi,
    GetDetailtDoctorById,
    StatisticalDoctorApi,
)
from src.apis.health_check import HealthCheck
from src.apis.medical_records_api import (
    GetMedicalRecordByAppointId,
    MedicalRecordsApiGET,
    MedicalRecordsApiPOST,
)
from src.apis.message_api import MessageApi
from src.apis.post_api import CommentApi, CreatePostApi, GetPostByIdApi
from src.apis.rating_api import RatingApi
from src.apis.user import ResetPassword, UserProfile
from src.apis.working_time_api import (
    CreateDoctorWorkingTimeApi,
    DoctorEmptyWorkingSchedulingTimeApi,
    DoctorWorkingTimeApi,
    DoctorWorkingTimeByIdApi,
    DoctorWorkingTimeOrderedApi,
)
from src.core.route import RouteSwagger

routes = [
    RouteSwagger("/health_check", HealthCheck, methods=["GET"], tags=["USER"]),
    # auth
    RouteSwagger("/auth/admin/register", AdminRegisterApi, tags=["ADMIN"]),
    RouteSwagger(
        "/auth/patient/register", PatientRegisterApi, methods=["POST"], tags=["PATIENT"]
    ),
    # local or foreign doctor
    # api will set verify_status = 2
    RouteSwagger(
        "/auth/doctor/register",
        DoctorLocalRegisterApi,
        methods=["POST"],
        tags=["ADMIN"],
    ),
    # api will set verify_status = 0
    RouteSwagger(
        "/auth/doctor/register/foreign",
        DoctorForeignRegisterApi,
        methods=["POST"],
        tags=["DOCTOR"],
    ),
    RouteSwagger(
        "/auth/doctor/verify/foreign",
        DoctorOtherVerifyApi,
        methods=["GET"],
        tags=["ADMIN"],
    ),
    RouteSwagger(
        "/admin/notify-register-mail",
        AdminNotifyRegisterMail,
        methods=["POST"],
        tags=["ADMIN"],
    ),
    RouteSwagger(
        "/admin/post",
        CreatePostApi,
        methods=["POST", "PUT"],
        tags=["ADMIN"],
    ),
    RouteSwagger(
        "/posts",
        CreatePostApi,
        methods=["GET"],
        tags=["USERS", "ADMIN", "DOCTOR", "PATIENT"],
    ),
    RouteSwagger(
        "/posts/{post_id}",
        GetPostByIdApi,
        methods=["GET"],
        tags=["USERS", "ADMIN", "DOCTOR", "PATIENT"],
    ),
    RouteSwagger(
        "/post/comment",
        CommentApi,
        methods=["POST", "PUT"],
        tags=["ADMIN", "PATIENT", "DOCTOR"],
    ),
    # change status verify doctor from 0 to -1
    RouteSwagger(
        "/auth/doctor/reject/foreign/{doctor_id}",
        DoctorForeignRejectApi,
        methods=["PUT"],
        tags=["ADMIN"],
    ),
    # change status verify doctor from 0 to 1
    RouteSwagger(
        "/auth/doctor/verify/foreign/{doctor_id}",
        DoctorOtherVerifyApiPut,
        methods=["PUT"],
        tags=["ADMIN"],
    ),
    # change status verify doctor from 1 to 2
    RouteSwagger(
        "/auth/doctor/verify/final",
        DoctorOtherVerifyFinalApiPut,
        methods=["PUT"],
        tags=["ADMIN"],
    ),
    RouteSwagger(
        "/auth/login", LoginApi, methods=["POST"], tags=["ADMIN", "PATIENT", "DOCTOR"]
    ),
    RouteSwagger(
        "/auth/logout", LogoutApi, methods=["POST"], tags=["ADMIN", "PATIENT", "DOCTOR"]
    ),
    # user detail
    RouteSwagger(
        "/user-settings/profile",
        UserProfile,
        methods=["PUT"],
        tags=["PATIENT", "DOCTOR"],
    ),
    RouteSwagger(
        "/user-settings/reset-password",
        ResetPassword,
        methods=["PUT"],
        tags=["PATIENT", "DOCTOR"],
    ),
    # Doctor api
    RouteSwagger(
        "/doctor/working-time",
        DoctorWorkingTimeApi,
        methods=["GET"],
        tags=["DOCTOR", "ADMIN", "PATIENT"],
    ),
    RouteSwagger(
        "/doctor/working-time",
        CreateDoctorWorkingTimeApi,
        methods=["POST"],
        tags=["ADMIN", "DOCTOR"],
    ),
    RouteSwagger(
        "/doctor/working-time/{id}",
        DoctorWorkingTimeByIdApi,
        methods=["GET"],
        tags=["ADMIN", "DOCTOR"],
    ),
    RouteSwagger(
        "/doctor/empty-working-hours",
        DoctorEmptyWorkingSchedulingTimeApi,
        methods=["GET"],
        tags=["DOCTOR", "ADMIN"],
    ),
    RouteSwagger(
        "/doctor/working-time/ordered",
        DoctorWorkingTimeOrderedApi,
        methods=["GET"],
        tags=["ADMIN", "PATIENT", "DOCTOR"],
    ),
    RouteSwagger(
        "/doctor",
        GetAllDoctorApi,
        methods=["GET"],
        tags=["DOCTOR", "PATIENT", "ADMIN", "USER"],
    ),
    RouteSwagger(
        "/doctor/patients",
        DoctorGetPatientsApi,
        methods=["GET"],
        tags=["DOCTOR", "ADMIN"],
    ),
    RouteSwagger(
        "/doctor/patient/{patient_id}",
        DoctorGetPatientsByIdApi,
        methods=["GET"],
        tags=["ADMIN", "DOCTOR"],
    ),
    RouteSwagger(
        "/doctor/local", GetAllDoctorLocalAPi, methods=["GET"], tags=["ADMIN"]
    ),
    RouteSwagger(
        "/doctor/foreign", GetAllDoctorForeignAPi, methods=["GET"], tags=["ADMIN"]
    ),
    RouteSwagger(
        "/doctor/{doctor_id}",
        GetDetailtDoctorById,
        methods=["GET"],
        tags=["PATIENT", "ADMIN", "DOCTOR", "USER"],
    ),
    # appointment api
    RouteSwagger(
        "/appointment", AppointmentApi, methods=["POST"], tags=["PATIENT", "ADMIN"]
    ),
    RouteSwagger(
        "/appointment",
        AppointmentApiGET,
        methods=["GET"],
        tags=["PATIENT", "ADMIN", "DOCTOR"],
    ),
    RouteSwagger(
        "/appointment/{appointment_id}/medical-record",
        GetMedicalRecordByAppointId,
        methods=["GET"],
        tags=["PATIENT", "ADMIN", "DOCTOR"],
    ),
    # medical api
    RouteSwagger(
        "/medical-record",
        MedicalRecordsApiGET,
        methods=["GET"],
        tags=["PATIENT", "ADMIN", "DOCTOR"],
    ),
    RouteSwagger(
        "/medical-record",
        MedicalRecordsApiPOST,
        methods=["POST", "PUT"],
        tags=["DOCTOR"],
    ),
    # thong ke
    RouteSwagger(
        "/statistical/doctor", StatisticalDoctorApi, methods=["GET"], tags=["ADMIN"]
    ),
    # chat bot
    RouteSwagger(
        "/bot-chat",
        BotServiceApi,
        methods=["GET"],
        tags=["USER", "PATIENT", "DOCTOR", "ADMIN"],
    ),
    # message
    RouteSwagger(
        "/conversation",
        ConversationApi,
        methods=["GET", "POST"],
        tags=["PATIENT", "DOCTOR", "ADMIN"],
    ),
    RouteSwagger(
        "/patient/daily-health-check",
        DailyDealthCheckApi,
        methods=["GET", "POST"],
        tags=["PATIENT", "DOCTOR", "ADMIN"],
    ),
    RouteSwagger(
        "/conversation",
        ConversationApi,
        methods=["GET", "POST"],
        tags=["PATIENT", "DOCTOR", "ADMIN"],
    ),
    RouteSwagger(
        "/message",
        MessageApi,
        methods=["GET", "POST"],
        tags=["PATIENT", "DOCTOR", "ADMIN"],
    ),
    # rating api
    RouteSwagger(
        "/rating",
        RatingApi,
        methods=["POST"],
        tags=["PATIENT", "DOCTOR", "ADMIN"],
    ),
]
