import logging as log

from src.core import HTTPEndpoint
from src.core.exception import BaseException, Forbidden, InternalServer
from src.core.security import JsonWebToken
from src.enum import ErrorCode, Role
from src.factory import Factory
from src.helper.doctor_helper import DoctorHelper
from src.schema.appointment_schema import RequestStatisticalAppointmentOrderSchema, RequestStatisticalAppointmentSchema
from src.schema.statistical_schema import StatisticalConversation, StatisticalPrice, StatisticalPriceAllDoctor, StatisticalPriceAllPatient, StatisticalPricePerson


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


class StatisticalAgeDistributionPatientApi(HTTPEndpoint):
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
            statistics = await patient_helper.age_distribution_patient()
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


class StatisticalAppointmentOrder(HTTPEndpoint):
    async def get(
        self, query_params: RequestStatisticalAppointmentOrderSchema, auth: JsonWebToken
    ):
        try:
            user_role:str = auth.get("role")
            user_id: int = auth.get("id")
            if user_role == Role.PATIENT.name or not user_id:
                raise Forbidden(
                    error_code=ErrorCode.FORBIDDEN.name,
                    errors={
                        "message": ErrorCode.msg_permission_denied.value,
                    },
                )
            user_id = query_params.user_id if user_role == Role.ADMIN.name else user_id
            from_date= query_params.from_date
            to_date= query_params.to_date
            appointment_helper = await Factory().get_appointment_helper()
            statistics = await appointment_helper.statistical_appointment_with_work(
                from_date=from_date, to_date=to_date, user_id=user_id
            )
            return statistics
        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            log.error(f"Error: {e}")
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            ) from e
class StatisticalConversationDoctorApi(HTTPEndpoint):
    async def get(self,query_params:StatisticalConversation  , auth: JsonWebToken):
        try:
            if auth.get("role") not in [Role.ADMIN.name, Role.DOCTOR.name]:
                raise Forbidden(
                    msg="Permission denied",
                    error_code=ErrorCode.FORBIDDEN.name,
                    errors={
                        "message": ErrorCode.msg_permission_denied.value,
                    },
                )
            if auth.get("role") == Role.DOCTOR.name:
                query_params.doctor_id = auth.get("id")
            doctor_helper: DoctorHelper = await Factory().get_doctor_helper()
            statistics = await doctor_helper.get_doctor_conversation_statistics(**query_params.model_dump())
            return statistics
        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            log.error(f"Error: {e}")
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            ) from e


class StatisticalPriceApi(HTTPEndpoint):
    async def get(self, query_params:StatisticalPrice,auth:JsonWebToken):
        try:
            if auth.get("role") != Role.ADMIN.name:
                raise Forbidden(
                    msg="Permission denied",
                    error_code=ErrorCode.FORBIDDEN.name,
                    errors={
                        "message": ErrorCode.msg_permission_denied.value,
                    },
                )

            appointment_helper = await Factory().get_appointment_helper()
            statistics = await appointment_helper.statistical_price(query_params.year)
            return statistics
        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            log.error(f"Error: {e}")
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            ) from e


class StatisticalPriceDoctorAllApi(HTTPEndpoint):
    async def get(self, query_params:StatisticalPriceAllDoctor,auth:JsonWebToken):
        try:
            if auth.get("role") != Role.ADMIN.name:
                raise Forbidden(
                    msg="Permission denied",
                    error_code=ErrorCode.FORBIDDEN.name,
                    errors={
                        "message": ErrorCode.msg_permission_denied.value,
                    },
                )

            appointment_helper = await Factory().get_appointment_helper()
            statistics = await appointment_helper.statistical_price_all_doctor(query_params.from_date, query_params.to_date)
            return statistics
        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            log.error(f"Error: {e}")
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            ) from e



class StatisticalPricePatientAllApi(HTTPEndpoint):
    async def get(self, query_params:StatisticalPriceAllPatient,auth:JsonWebToken):
        try:
            if auth.get("role") != Role.ADMIN.name:
                raise Forbidden(
                    msg="Permission denied",
                    error_code=ErrorCode.FORBIDDEN.name,
                    errors={
                        "message": ErrorCode.msg_permission_denied.value,
                    },
                )

            appointment_helper = await Factory().get_appointment_helper()
            statistics = await appointment_helper.statistical_price_all_patient(query_params.from_date, query_params.to_date)
            return statistics
        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            log.error(f"Error: {e}")
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            ) from e
class StatisticalPricePersonApi(HTTPEndpoint):
    async def get(self, query_params:StatisticalPricePerson,auth:JsonWebToken):
        try:
            user_id = query_params.user_id if auth.get("role") == Role.ADMIN.name else auth.get("id")
            if not user_id:
                raise Forbidden(
                    error_code=ErrorCode.BAD_REQUEST.name,
                    errors={
                        "message": ErrorCode.msg_user_id_is_required.value,
                    },
                )
            appointment_helper = await Factory().get_appointment_helper()
            from_date= query_params.from_date
            to_date= query_params.to_date
            _result = await appointment_helper.statistical_price_person(from_date, to_date, user_id)
            return _result
        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            log.error(f"Error: {e}")
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            ) from e
