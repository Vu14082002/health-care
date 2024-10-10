from starlette.routing import WebSocketRoute

from src.apis.appointment import AppointmentApi, AppointmentApiGET
from src.apis.auth import (
    AdminRegisterApi,
    DoctorForeignRegisterApi,
    DoctorLocalRegisterApi,
    DoctorOtherVerifyApi,
    DoctorOtherVerifyApiPut,
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
from src.apis.socket import MessageSocket, OnlineUser, OpenConversation
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
    RouteSwagger(
        "/auth/patient/register", PatientRegisterApi, methods=["POST"], tags=["PATIENT"]
    ),
    RouteSwagger(
        "/auth/doctor/register/foreign",
        DoctorForeignRegisterApi,
        methods=["POST"],
        tags=["DOCTOR"],
    ),
    RouteSwagger(
        "/auth/doctor/register",
        DoctorLocalRegisterApi,
        methods=["POST"],
        tags=["ADMIN"],
    ),
    RouteSwagger("/auth/admin/register", AdminRegisterApi, tags=["ADMIN"]),
    RouteSwagger(
        "/auth/doctor/verify/foreign",
        DoctorOtherVerifyApi,
        methods=["GET"],
        tags=["ADMIN"],
    ),
    RouteSwagger(
        "/auth/doctor/verify/foreign/{doctor_id}",
        DoctorOtherVerifyApiPut,
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
        "/user_settings/profile",
        UserProfile,
        methods=["PUT"],
        tags=["PATIENT", "DOCTOR"],
    ),
    RouteSwagger(
        "/user_settings/reset-password",
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
    # websocker
    WebSocketRoute(
        "/ws/online",
        OnlineUser,
    ),
    WebSocketRoute(
        "/ws/conversation",
        OpenConversation,
    ),
    WebSocketRoute("/ws/message", MessageSocket),
    # WebSocketRoute("/ws/call", MessageSocket),
]
