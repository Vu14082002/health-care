import logging as log

from src.core import HTTPEndpoint
from src.core.exception import BadRequest, Forbidden, InternalServer
from src.core.security import JsonWebToken
from src.core.security.authentication import JsonWebToken
from src.enum import ErrorCode, Role
from src.factory import Factory
from src.helper.appointment_helper import AppointmentHelper
from src.helper.doctor_helper import DoctorHelper
from src.models.appointment_model import AppointmentModel
from src.schema.appointment_schema import RequestRegisterAppointment
from src.schema.doctor_schema import (RequestDetailDoctorSchema,
                                      RequestDoctorWorkScheduleNextWeek,
                                      RequestGetAllDoctorsSchema,
                                      RequestGetUncenteredTimeSchema,
                                      RequestGetWorkingTimeSchema,
                                      RequestUpdateDoctorSchema,
                                      RequestUpdatePathParamsSchema)


class AppointmentApi(HTTPEndpoint):
    async def get(self, auth: JsonWebToken):
        return {"message": "not implemented"}

    async def post(self, form_data: RequestRegisterAppointment, auth: JsonWebToken):
        try:
            user_role = auth.get("role", "")
            if user_role not in ["ADMIN", "PATIENT"]:
                raise Forbidden(msg="Unauthorized access",
                                error_code=ErrorCode.UNAUTHORIZED.name,
                                errors={"message": "Only patients or admins can create appointments"})

            appointment_helper: AppointmentHelper = await Factory().get_appointment_helper()

            if user_role == "ADMIN" and not form_data.patient_id:
                raise Forbidden(msg="Unauthorized access",
                                error_code=ErrorCode.UNAUTHORIZED.name,
                                errors={"message": "patient_id is required for admin"})
            patient_id = form_data.patient_id if user_role == "ADMIN" else auth.get(
                "id")
            response_data = await appointment_helper.create_appointment(patient_id, form_data.doctor_id, form_data.work_schedule_id, form_data.pre_examination_notes)
            return response_data
        except (BadRequest, Forbidden) as e:
            raise e
        except Exception as e:
            raise InternalServer(msg="Internal server error",
                                 error_code=ErrorCode.SERVER_ERROR.name) from e
