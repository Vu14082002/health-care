from src.apis.appointment import AppointmentApi, AppointmentApiGET
from src.apis.auth import (AdminRegisterApi, DoctorForeignRegisterApi,
                           DoctorLocalRegisterApi, DoctorOtherVerifyApi,
                           LoginApi, LogoutApi, PatientRegisterApi)
from src.apis.docter_api import (CreateDoctorWorkingTimeApi,
                                 DoctorEmptyWorkingSchedulingTimeApi,
                                 DoctorWorkingTimeApi, GetAllDoctorApi,
                                 GetDetailtDoctorById)
from src.apis.health_check import HealthCheck
from src.core.route import RouteSwagger

routes = [

    RouteSwagger("/health_check", HealthCheck, methods=["GET"], tags=["User"]),

    # auth
    RouteSwagger("/auth/patient/register", PatientRegisterApi,
                 methods=["POST"], tags=["PATIENT"]),

    RouteSwagger("/auth/doctor/register/foreign", DoctorForeignRegisterApi,
                 methods=["POST"], tags=["DOCTOR"]),

    RouteSwagger("/auth/doctor/register/local", DoctorLocalRegisterApi,
                 methods=["POST"], tags=["ADMIN"]),

    # RouteSwagger("/auth/doctor/register/offline", DoctorOfflineRegisterApi,
    #              methods=["POST"], tags=["ADMIN"]),

    # RouteSwagger("/auth/doctor/register/both", DoctorBothRegisterApi,
    #              methods=["POST"], tags=["ADMIN"]),

    RouteSwagger("/auth/admin/register", AdminRegisterApi,
                 tags=["ADMIN"]),

    RouteSwagger("/auth/doctor/verify/other", DoctorOtherVerifyApi,
                 methods=["GET", "PUT"], tags=["ADMIN"]),

    RouteSwagger("/auth/login", LoginApi,
                 methods=["POST"],  tags=["ADMIN", "PATIENT", "DOCTOR"]),

    RouteSwagger("/auth/logout", LogoutApi,
                 methods=["POST"],  tags=["ADMIN", "PATIENT", "DOCTOR"]),

    # Doctor api
    # TODO: pass 1
    RouteSwagger("/doctor", GetAllDoctorApi,
                 methods=["GET"], tags=["DOCTOR", "PATIENT", "ADMIN", "USER"]),
    RouteSwagger(
        f"/doctor/{{doctor_id}}",
        GetDetailtDoctorById,
        methods=["GET"],
        tags=["PATIENT", "ADMIN", "DOCTOR"]
    ),
    # RouteSwagger(
    #     "/doctor",
    #     GetDetailtDoctorById,
    #     methods=["PUT"],
    #     tags=["ADMIN", "DOCTOR"]
    # ),
    RouteSwagger(
        "/doctor/working-time",
        DoctorWorkingTimeApi,
        methods=["GET"],
        tags=["ADMIN", "PATIENT", "DOCTOR"]
    ),
    RouteSwagger(
        "/doctor/working-time",
        CreateDoctorWorkingTimeApi,
        methods=["POST"],
        tags=["DOCTOR", "ADMIN"]
    ),
    RouteSwagger(
        "/doctor/empty-working-hours",
        DoctorEmptyWorkingSchedulingTimeApi,
        methods=["GET"],
        tags=["DOCTOR", "ADMIN"]
    ),
    # appointment api
    RouteSwagger(
        "/appointment",
        AppointmentApi,
        methods=["POST"],
        tags=["PATIENT", "ADMIN"]
    ),
    RouteSwagger(
        "/appointment",
        AppointmentApiGET,
        methods=["GET"],
        tags=["PATIENT", "ADMIN", "DOCTOR"]
    ),
]
