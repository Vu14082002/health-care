from src.apis.appointment import AppointmentApi, AppointmentApiGET
from src.apis.auth import (AdminRegisterApi, DoctorForeignRegisterApi,
                           DoctorLocalRegisterApi, DoctorOtherVerifyApi,
                           DoctorOtherVerifyApiPut, LoginApi, LogoutApi,
                           PatientRegisterApi)
from src.apis.docter_api import (GetAllDoctorApi, GetAllDoctorForeignAPi,
                                 GetAllDoctorLocalAPi, GetDetailtDoctorById,
                                 StatisticalDoctorApi)
from src.apis.health_check import HealthCheck
from src.apis.medical_records_api import (MedicalRecordsApiGET,
                                          MedicalRecordsApiPOST)
from src.apis.working_time_api import (CreateDoctorWorkingTimeApi,
                                       DoctorEmptyWorkingSchedulingTimeApi,
                                       DoctorWorkingTimeApi)
from src.core.route import RouteSwagger

routes = [

    RouteSwagger("/health_check", HealthCheck, methods=["GET"], tags=["USER"]),

    # auth
    RouteSwagger("/auth/patient/register", PatientRegisterApi,
                 methods=["POST"], tags=["PATIENT"]),

    RouteSwagger("/auth/doctor/register/foreign", DoctorForeignRegisterApi,
                 methods=["POST"], tags=["DOCTOR"]),

    RouteSwagger("/auth/doctor/register", DoctorLocalRegisterApi,
                 methods=["POST"], tags=["ADMIN"]),

    RouteSwagger("/auth/admin/register", AdminRegisterApi,
                 tags=["ADMIN"]),

    RouteSwagger("/auth/doctor/verify/foreign", DoctorOtherVerifyApi,
                 methods=["GET"], tags=["ADMIN"]),

    RouteSwagger(f"/auth/doctor/verify/foreign/{{doctor_id}}", DoctorOtherVerifyApiPut,
                 methods=["PUT"], tags=["ADMIN"]),

    RouteSwagger("/auth/login", LoginApi,
                 methods=["POST"],  tags=["ADMIN", "PATIENT", "DOCTOR"]),

    RouteSwagger("/auth/logout", LogoutApi,
                 methods=["POST"],  tags=["ADMIN", "PATIENT", "DOCTOR"]),

    # Doctor api

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
    RouteSwagger("/doctor", GetAllDoctorApi,
                 methods=["GET"], tags=["DOCTOR", "PATIENT", "ADMIN", "USER"]),

    RouteSwagger("/doctor/local", GetAllDoctorLocalAPi,
                 methods=["GET"], tags=["ADMIN"]),

    RouteSwagger("/doctor/foreign", GetAllDoctorForeignAPi,
                 methods=["GET"], tags=["ADMIN"]),
    RouteSwagger(
        "/doctor/{doctor_id}",
        GetDetailtDoctorById,
        methods=["GET"],
        tags=["PATIENT", "ADMIN", "DOCTOR"]
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
    # medical api
    RouteSwagger(
        "/medical-record",
        MedicalRecordsApiGET,
        methods=["GET"],
        tags=["PATIENT", "ADMIN", "DOCTOR"]
    ),
    RouteSwagger(
        "/medical-record",
        MedicalRecordsApiPOST,
        methods=["POST"],
        tags=["DOCTOR"]
    ),

    # thong ke
    RouteSwagger(
        "/statistical/doctor",
        StatisticalDoctorApi,
        methods=["GET"],
        tags=["ADMIN"]
    ),
]
