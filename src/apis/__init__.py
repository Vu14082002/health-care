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
from src.apis.docter_api import (
    DoctorGetPatientsApi,
    GetAllDoctorApi,
    GetAllDoctorForeignAPi,
    GetAllDoctorLocalAPi,
    GetDetailtDoctorById,
    StatisticalDoctorApi,
)
from src.apis.health_check import HealthCheck
from src.apis.medical_records_api import MedicalRecordsApiGET, MedicalRecordsApiPOST
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
        f"/auth/doctor/verify/foreign/{{doctor_id}}",
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
        f"/doctor/working-time/{{id}}",
        DoctorWorkingTimeByIdApi,
        methods=["GET"],
        tags=["ADMIN", "DOCTOR"],
    ),
    #  day la api lay danh sach gio lam viec con trong cua bac si trong tuan
    RouteSwagger(
        "/doctor/empty-working-hours",
        DoctorEmptyWorkingSchedulingTimeApi,
        methods=["GET"],
        tags=["DOCTOR", "ADMIN"],
    ),
    # day la api lay danh cac lioc lam viec cua bac si da dc order
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
    # medical api
    RouteSwagger(
        "/medical-record",
        MedicalRecordsApiGET,
        methods=["GET"],
        tags=["PATIENT", "ADMIN", "DOCTOR"],
    ),
    RouteSwagger(
        "/medical-record", MedicalRecordsApiPOST, methods=["POST"], tags=["DOCTOR"]
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
]
