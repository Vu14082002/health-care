import logging as log

from src.core import HTTPEndpoint
from src.core.exception import BaseException, Forbidden, InternalServer
from src.core.security import JsonWebToken
from src.enum import ErrorCode, Role
from src.factory import Factory
from src.helper.doctor_helper import DoctorHelper
from src.schema.appointment_schema import RequestStatisticalAppointmentSchema


class StatisticalCountPatientApi(HTTPEndpoint):
    async def get(self, auth: JsonWebToken):
        try:
            if auth.get("role") != Role.ADMIN.name:
                raise Forbidden(
                    msg="Permission denied",
                    error_code=ErrorCode.FORBIDDEN.name,
                    errors={
                        "message": ErrorCode.msg_permission_denied.value,
                    },
                )

            patient_helper = await Factory().get_patient_helper()
            statistics = await patient_helper.count_patient()
            return statistics
        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            log.error(f"Error: {e}")
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            ) from e


class StatisticalDoctorApi(HTTPEndpoint):
    async def get(self, auth: JsonWebToken):
        try:
            if auth.get("role") != Role.ADMIN.name:
                raise Forbidden(
                    msg="Permission denied",
                    error_code=ErrorCode.FORBIDDEN.name,
                    errors={
                        "message": ErrorCode.msg_permission_denied.value,
                    },
                )

            doctor_helper: DoctorHelper = await Factory().get_doctor_helper()
            statistics = await doctor_helper.get_doctor_statistics()
            return statistics
        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            log.error(f"Error: {e}")
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            ) from e


# appointment statistical
class StatisticalAppointment(HTTPEndpoint):

    async def get(
        self, query_params: RequestStatisticalAppointmentSchema, auth: JsonWebToken
    ):
        try:
            if auth.get("role") != Role.ADMIN.name:
                raise Forbidden(
                    error_code=ErrorCode.FORBIDDEN.name,
                    errors={
                        "message": ErrorCode.msg_permission_denied.value,
                    },
                )
            year = query_params.year
            appointment_helper = await Factory().get_appointment_helper()
            statistics = await appointment_helper.statistical_appointment(year)
            return statistics
        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            log.error(f"Error: {e}")
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            ) from e
