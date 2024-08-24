
from src.apis.auth import (AdminRegisterApi, DoctorPatientRegisterApi,
                           LoginApi, PatientRegisterApi)
from src.apis.docker_api import GetAllDoctorApi, GetDetailtDoctorById
from src.apis.health_check import HealthCheck
from src.core.route import RouteSwagger

routes = [
    # auth api : OKE
    RouteSwagger("/health_check", HealthCheck, methods=["GET"], tags=["User"]),
    RouteSwagger("/auth/patient/register", PatientRegisterApi,
                 methods=["POST"], tags=["PATIENT"]),
    RouteSwagger("/auth/doctor/register", DoctorPatientRegisterApi,
                 methods=["POST"], tags=["DOCTOR"]),
    RouteSwagger("/auth/admin/register", AdminRegisterApi,
                 tags=["ADMIN"]),
    RouteSwagger("/auth/login", LoginApi,
                 methods=["POST"], tags=["ADMIN,PATIENT,DOCTOR"]),

    # Doctor api
    RouteSwagger("/doctor", GetAllDoctorApi,
                 methods=["GET"], tags=["DOCTOR,PATIENT,ADMIN"]),
    RouteSwagger(
        "/doctor/{doctor_id}",
        GetDetailtDoctorById,
        methods=["GET"],
        tags=["DOCTOR,PATIENT,ADMIN"]
    ),
]
