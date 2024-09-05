from src.apis.auth import (AdminRegisterApi, DoctorBothRegisterApi,
                           DoctorOfflineRegisterApi, DoctorOnlineRegisterApi,
                           DoctorOtherRegisterApi, LoginApi, LogoutApi,
                           PatientRegisterApi)
from src.apis.docter_api import (DoctorWorkingTimeApi, GetAllDoctorApi,
                                 GetDetailtDoctorById)
from src.apis.health_check import HealthCheck
from src.core.route import RouteSwagger

routes = [

    RouteSwagger("/health_check", HealthCheck, methods=["GET"], tags=["User"]),

    # auth
    RouteSwagger("/auth/doctor/register/other", DoctorOtherRegisterApi,
                 methods=["POST"], tags=["USER"]),

    RouteSwagger("/auth/patient/register", PatientRegisterApi,
                 methods=["POST"], tags=["PATIENT"]),
    # doctor register
    RouteSwagger("/auth/doctor/register/online", DoctorOnlineRegisterApi,
                 methods=["POST"], tags=["ADMIN"]),

    RouteSwagger("/auth/doctor/register/offline", DoctorOfflineRegisterApi,
                 methods=["POST"], tags=["ADMIN"]),

    RouteSwagger("/auth/doctor/register/both", DoctorBothRegisterApi,
                 methods=["POST"], tags=["ADMIN"]),


    RouteSwagger("/auth/admin/register", AdminRegisterApi,
                 tags=["ADMIN"]),

    RouteSwagger("/auth/login", LoginApi,
                 methods=["POST"], tags=["ADMIN,PATIENT,DOCTOR"]),
    RouteSwagger("/auth/logout", LogoutApi,
                 methods=["POST"], tags=["ADMIN,PATIENT,DOCTOR"]),
    # Doctor api
    RouteSwagger("/doctor", GetAllDoctorApi,
                 methods=["GET"], tags=["DOCTOR"]),
    RouteSwagger(
        "/doctor/{doctor_id}",
        GetDetailtDoctorById,
        methods=["GET"],
        tags=["DOCTOR,PATIENT,ADMIN"]
    ),
    RouteSwagger(
        "/doctor/{doctor_id}",
        GetDetailtDoctorById,
        methods=["PUT"],
        tags=["DOCTOR,ADMIN"]
    ),
    RouteSwagger(
        "/doctor/working-time",
        DoctorWorkingTimeApi,
        methods=["POST"],
        tags=["DOCTOR"]
    ),
    RouteSwagger(
        "/doctor/working-time",
        DoctorWorkingTimeApi,
        methods=["GET"],
        tags=["ADMIN,PATIENT,DOCTOR"]
    ),
]
