
from src.apis.auth import (AdminRegisterApi, DoctorPatientRegisterApi,
                           LoginApi, PatientRegisterApi)
from src.apis.docker_api import DoctorApi
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
    RouteSwagger("/doctor", DoctorApi,
                 methods=["GET"], tags=["DOCTOR,PATIENT,ADMIN"]),
]
