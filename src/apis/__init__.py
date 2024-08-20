
from src.apis.auth import DoctorRegisterApi, LoginApi, RegisterApi
from src.apis.health_check import HealthCheck
from src.core.route import RouteSwagger

routes = [
    RouteSwagger("/health_check", HealthCheck, methods=["GET"], tags=["User"]),
    RouteSwagger("/auth/patient/register", RegisterApi,
                 methods=["POST"], tags=["PATIENT"]),
    RouteSwagger("/auth/doctor/register", DoctorRegisterApi,
                 methods=["POST"], tags=["PATIENT"]),
    RouteSwagger("/auth/login", LoginApi,
                 methods=["POST"], tags=["ADMIN,PATIENT,DOCTOR"]),
]
