from enum import Enum

from pydantic import BaseModel


class ErrorCode(Enum):
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    AUTHEN_FAIL = "AUTHEN_FAIL"
    BAD_REQUEST = "BAD_REQUEST"
    FORBIDDEN = "FORBIDDEN"
    SERVER_ERROR = "SERVER_ERROR"
    NOT_FOUND = "NOT_FOUND"
    METHOD_NOT_ALLOW = "METHOD_NOT_ALLOW"
    UNAUTHORIZED = "UNAUTHORIZED"
    CONFLICT = "CONFLICT"
    SIGNATURE_VERIFY_FAIL = "SIGNATURE_VERIFY_FAIL"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    USER_HAVE_BEEN_REGISTERED = "USER_HAVE_BEEN_REGISTERED"
    PHONE_OR_EMAIL_HAVE_BEEN_REGISTERED = "PHONE_OR_EMAIL_HAVE_BEEN_REGISTERED"
    ROLE_NOT_FOUND = "ROLE_NOT_FOUND"
    INVALID_PARAMETER = "INVALID_PARAMETER"
    EMAIL_HAVE_BEEN_REGISTERED = "EMAIL_HAVE_BEEN_REGISTERED"
    LICENSE_NUMBER_HAVE_BEEN_REGISTERED = "LICENSE_NUMBER_HAVE_BEEN_REGISTERED"
    EMAIL_OR_LICENSE_NUMBER_HAVE_BEEN_REGISTERED = (
        "EMAIL_OR_LICENSE_NUMBER_HAVE_BEEN_REGISTERED"
    )
    DOCTOR_NOT_FOUND = "DOCTOR_NOT_FOUND"
    INVALID_EXAMINATION_TYPE = "INVALID_EXAMINATION_TYPE"
    SCHEDULE_CONFLICT = "SCHEDULE_CONFLICT"
    ALLREADY_ORDERED = "ALLREADY_ORDERED"
    msg_server_error = "Server is error, pls try later"
    INVALID_APPOINTMENT = "INVALID_APPOINTMENT"
    WORK_SCHEDULE_NOT_FOUND = "WORK_SCHEDULE_NOT_FOUND"
    MEDICAL_RECORD_EXIST = "MEDICAL_RECORD_EXIST"
    YOU_HAVE_NOT_COMPLETE_OTHER_APPOINTMENT = "YOU_HAVE_NOT_COMPLETE_OTHER_APPOINTMENT"
    INVALID_MEDICAL_RECORD = "INVALID_MEDICAL_RECORD"
    PATIENT_NOT_FOUND = "PATIENT_NOT_FOUND"
    DATABASE_ERROR = "DATABASE_ERROR"
    INVALID_FILE_TYPE = "INVALID_FILE_TYPE"
    INVALID_REQUEST = "INVALID_REQUEST"
    msg_permission_denied = "You don't have permission to access this resource"
    msg_delete_account_before = "Your account has been deleted before, if you want to use this account, please contact the admin"
    msg_wrong_password = "Wrong password"
    msg_phone_not_registered = "Phone number is not registered"
    msg_verify_step_one_befor_verify_two = (
        "You must verify doctor with status 1 before verify with status 2"
    )


CACHE_REFRESH_TOKEN = 60 * 60 * 5
CACHE_ACCESS_TOKEN = 60 * 60 * 5
KEY_CACHE_LOGOUT = "logout"


class Role(Enum):
    ADMIN = "ADMIN"
    DOCTOR = "DOCTOR"
    PATIENT = "PATIENT"


class TypeOfDisease(Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    BOTH = "both"


class AppointmentModelStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    PROCESSING = "processing"


class MessageContentSchema(BaseModel):
    media: str | bytes | None
    images: list[str] | list[bytes] | None
    content: str | None


class ImageDailyHealthCheck(BaseModel):
    image_url: str
    image_name: str | None = None
    image_size: float | None = None


class ArrayImageDailyHealthCheck(BaseModel):
    images: list[ImageDailyHealthCheck]
