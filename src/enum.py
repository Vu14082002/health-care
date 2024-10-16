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
    INVALID_APPOINTMENT = "INVALID_APPOINTMENT"
    WORK_SCHEDULE_NOT_FOUND = "WORK_SCHEDULE_NOT_FOUND"
    MEDICAL_RECORD_EXIST = "MEDICAL_RECORD_EXIST"
    YOU_HAVE_NOT_COMPLETE_OTHER_APPOINTMENT = "YOU_HAVE_NOT_COMPLETE_OTHER_APPOINTMENT"
    INVALID_MEDICAL_RECORD = "INVALID_MEDICAL_RECORD"
    PATIENT_NOT_FOUND = "PATIENT_NOT_FOUND"
    DATABASE_ERROR = "DATABASE_ERROR"
    INVALID_FILE_TYPE = "INVALID_FILE_TYPE"
    INVALID_REQUEST = "INVALID_REQUEST"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    msg_permission_denied = "Bạn không có quyền truy cập tài nguyên này"
    msg_delete_account_before = "Tài khoản của bạn đã bị xóa trước đó, nếu bạn muốn sử dụng tài khoản này vui lòng liên hệ với quản trị viên"
    msg_wrong_password = "Mật khẩu sai"
    msg_phone_not_registered = "Phone number is not registered"
    msg_error_login = "Phone number or password is incorrect"
    msg_server_error = "Máy chủ bị lỗi, vui lòng thử lại sau"
    msg_permission_rating = (
        "Bạn phải có và thực hiện cuộc hẹn với bác sĩ trước khi bình luận"
    )

    msg_verify_step_one_befor_verify_two = (
        "Bạn phải xác minh bác sĩ ở trạng thái 1 trước khi xác minh ở trạng thái 2"
    )
    msg_invalid_medical_record = "media must be file"
    msg_server_error_procesing = (
        " Máy chủ lỗi khi thực hiện tác vụ này, vui lòng thử lại sau"
    )
    msg_doctor_not_found_or_verify_status_1 = (
        "Không tìm thấy bác sĩ hoặc đã được xác minh ở trạng thái 1"
    )
    msg_doctor_not_found_or_verify_status_2 = (
        "Không tìm thấy bác sĩ hoặc đã được xác minh ở trạng thái 2"
    )
    msg_doctor_not_found_or_reject = (
        "Không tìm thấy bác sĩ hoặc đã được xác minh ở trạng thái -1"
    )
    msg_content_message_required = (
        "Phải cung cấp ít nhất một trong các, content, media, or image"
    )
    msg_content_message_or_title_required = (
        "Phải cung cấp ít nhất một trong các, content, media, or title"
    )
    msg_only_support_patient = "Tính năng này hiện chỉ hỗ trợ cho bệnh nhân"
    msg_you_have_not_complete_other_appointment = (
        "Bạn phải hoàn thành cuộc hẹn với bác sĩ trước khi đặt thêm lịch hẹn khác"
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
    @classmethod
    def all_statuses(cls):
        return [status.value for status in cls]


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
