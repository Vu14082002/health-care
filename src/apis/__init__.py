
from src.apis.auth import (AdminRegisterApi, DoctorPatientRegisterApi,
                           LoginApi, PatientRegisterApi)
from src.apis.health_check import HealthCheck
from src.core.route import RouteSwagger

routes = [
    # register route
    RouteSwagger("/health_check", HealthCheck, methods=["GET"], tags=["User"]),
    RouteSwagger("/auth/patient/register", PatientRegisterApi,
                 methods=["POST"], tags=["PATIENT"]),
    RouteSwagger("/auth/doctor/register", DoctorPatientRegisterApi,
                 methods=["POST"], tags=["DOCOTR"]),
    RouteSwagger("/auth/admin/register", AdminRegisterApi,
                 tags=["ADMIN"]),
    # login route
    RouteSwagger("/auth/login", LoginApi,
                 methods=["POST"], tags=["ADMIN,PATIENT,DOCTOR"]),
]
