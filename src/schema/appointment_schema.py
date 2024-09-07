

from pydantic import BaseModel


class RequestRegisterAppointment(BaseModel):
    patient_id: int | None = None
    doctor_id: int
    work_schedule_id: int
    pre_examination_notes: str | None = None
