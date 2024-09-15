import logging as log

from src.core import HTTPEndpoint
from src.core.exception import BadRequest, Forbidden, InternalServer
from src.core.security.authentication import JsonWebToken
from src.enum import ErrorCode, Role
from src.factory import Factory
from src.helper.appointment_helper import AppointmentHelper
from src.helper.doctor_helper import DoctorHelper
from src.models.appointment_model import AppointmentModel
from src.schema.appointment_schema import (RequestGetAllAppointmentSchema,
                                           RequestRegisterAppointment)
from src.schema.doctor_schema import (RequestDetailDoctorSchema,
                                      RequestDoctorWorkScheduleNextWeek,
                                      RequestGetAllDoctorsSchema,
                                      RequestGetUncenteredTimeSchema,
                                      RequestGetWorkingTimeSchema,
                                      RequestUpdateDoctorSchema,
                                      RequestUpdatePathParamsSchema)


class AppointmentApiGET(HTTPEndpoint):
    async def get(self, query_params: RequestGetAllAppointmentSchema, auth: JsonWebToken):
        try:
            appointment_helper: AppointmentHelper = await Factory().get_appointment_helper()
            user_role = auth.get("role", "")
            user_id = auth.get("id")

            if user_role not in [Role.ADMIN.value, Role.DOCTOR.value, Role.PATIENT.value]:
                raise Forbidden(msg="Unauthorized access",
                                error_code=ErrorCode.UNAUTHORIZED.name)

            filter_params = query_params.model_dump()
            appointments = {}
            if user_role == Role.ADMIN.value:
                appointments = await appointment_helper.get_all_appointments(**filter_params)
            elif user_role == Role.DOCTOR.value:
                # Doctor can only see their own appointments
                filter_params["doctor_id"] = user_id
                appointments = await appointment_helper.get_all_appointments(**filter_params)
            elif user_role == Role.PATIENT.value:
                filter_params["patient_id"] = user_id
                appointments = await appointment_helper.get_all_appointments(**filter_params)
            return appointments
        except Forbidden as e:
            log.error(e)
            raise e
        except Exception as e:
            log.error(e)
            raise InternalServer(msg="Internal server error",
                                 error_code=ErrorCode.SERVER_ERROR.name, errors={"message": "server is error, please try later"}) from e


class AppointmentApi(HTTPEndpoint):
    async def post(self, form_data: RequestRegisterAppointment, auth: JsonWebToken):
        try:
            user_role = auth.get("role", "")
            if user_role not in ["ADMIN", "PATIENT"]:
                raise Forbidden(msg="Unauthorized access",
                                error_code=ErrorCode.UNAUTHORIZED.name,
                                errors={"message": "Only patients or admins can create appointments"})

            if user_role == "ADMIN" and not form_data.patient_id:
                raise Forbidden(msg="Unauthorized access",
                                error_code=ErrorCode.UNAUTHORIZED.name,
                                errors={"message": "patient_id is required for admin"})
            patient_id = form_data.patient_id if user_role == "ADMIN" else auth.get(
                "id")
            appointment_helper: AppointmentHelper = await Factory().get_appointment_helper()
            response_data = await appointment_helper.create_appointment(patient_id, form_data.doctor_id, form_data.work_schedule_id, form_data.pre_examination_notes)
            return response_data
        except (BadRequest, Forbidden) as e:
            raise e
        except Exception as e:
            log.error(e)
            raise InternalServer(msg="Internal server error",
                                 error_code=ErrorCode.SERVER_ERROR.name) from e
