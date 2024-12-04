from enum import Enum
from typing import Final

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
    S3_UPLOAD_ERROR = "S3_UPLOAD_ERROR"
    YOU_HAVE_NOT_COMPLETE_OTHER_APPOINTMENT = "YOU_HAVE_NOT_COMPLETE_OTHER_APPOINTMENT"
    INVALID_MEDICAL_RECORD = "INVALID_MEDICAL_RECORD"
    PATIENT_NOT_FOUND = "PATIENT_NOT_FOUND"
    DATABASE_ERROR = "DATABASE_ERROR"
    INVALID_FILE_TYPE = "INVALID_FILE_TYPE"
    INVALID_REQUEST = "INVALID_REQUEST"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    PAYMENT_REQUIRED="PAYMENT_REQUIRED"
    PAYMENT_CONTENT_ERROR="PAYMENT_CONTENT_ERROR"
    msg_user_id_is_required = "Phải cung cấp mã người dùng để thực hiện hành động này"
    msg_user_not_found = "Tài khoản không tồn tại"
    msg_permission_denied = "Bạn không có quyền truy cập tài nguyên này"
    msg_delete_account_before = "Tài khoản của bạn đã bị xóa trước đó, nếu bạn muốn sử dụng tài khoản này vui lòng liên hệ với quản trị viên"
    msg_wrong_password = "Mật khẩu sai"
    msg_phone_not_registered = "Số điện thoại chưa được đăng ký"
    msg_phone_have_been_registered = "Số điện thoại đã được đăng ký"
    msg_email_have_been_registered = "Email đã được đăng ký"
    msg_error_login = "Sai tài khoản hoặc mật khẩu"
    msg_server_error = "Máy chủ bị lỗi, vui lòng thử lại sau"
    msg_s3_error = "Lỗi khi tải file lên hệ thống"
    msg_payment_content_error = "Nội dung thanh toán không hợp lệ"
    msg_email_or_license_number_have_been_registered = (
        "Email hoặc số mã số bác sĩ này đã được đăng ký"
    )
    msg_permission_rating = (
        "Bạn phải có và thực hiện cuộc hẹn với bác sĩ trước khi bình luận"
    )

    msg_verify_step_one_before_verify_two = (
        "Bạn phải xác minh bác sĩ ở trạng thái 1 trước khi xác minh ở trạng thái 2"
    )
    msg_invalid_medical_record = "media phải là file"
    msg_server_error_procesing = (
        " Máy chủ lỗi khi thực hiện tác vụ này, vui lòng thử lại sau"
    )
    msg_doctor_not_found_or_verify_status_1 = (
        "Không tìm thấy bác sĩ hoặc đã được xác minh ở trạng thái 1"
    )
    msg_doctor_not_verify_to_create_working = "Bác sĩ chưa được xác minh ở bước 2 vì thế không thể thực hiện tạo lịch làm việc"
    msg_doctor_not_found_or_verify_status_2 = (
        "Không tìm thấy bác sĩ hoặc đã được xác minh ở trạng thái 2"
    )
    msg_doctor_not_found_or_reject = (
        "Không tìm thấy bác sĩ hoặc bác sĩ đã bị từ chối tham gia vào hệ thống"
    )
    msg_doctor_not_found = (
        "Không tìm thấy bác sĩ"
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
    msg_incorrect_old_password = "Mật khẩu cũ không chính xác",
    msg_patient_id_is_required = "Phải cung cấp mã bênh nhân để thực hiên hành động này"
    msg_cancel_appointment: str = "Hủy cuộc hẹn thành công"
    msg_create_appointment_successfully = "Tạo cuộc hẹn thành công"
    msg_not_found_appointment = "Không tìm thấy cuộc hẹn phù hợp với yêu cầu của bạn"
    msg_not_caceled_appointment_alrealdy_finish = "Cuộc hẹn đã hoàn thành không thể hủy"
    msg_appointment_already_order = (
        "Cuộc hẹn này đã được đặt, vui lòng chọn cuộc hẹn khác"
    )
    msg_not_caceled_appointment_less_than_48_hours= "Cuộc hẹn không thể hủy khi còn ít hơn 48 giờ"
    msg_delete_appointment_successfully = "Hủy cuộc hẹn thành công"
    msg_can_not_delete_comment = "Bạn không thể thực hiện hành động xóa binh luận này"
    # post message
    msg_post_not_found = "Không tìm thấy bài viết hoặc bài viết đã bị xóa từ trước"
    msg_comment_not_found = "Không tìm thấy bình luận hoặc bình luận đã bị xóa từ trước"
    msg_create_post_successfully = "Tạo bài viết thành công"
    msg_update_post_successfully = "Cập nhật bài viết thành công"
    msg_delete_post_successfully = "Xóa bài viết thành công"
    msg_create_comment_successfully = "Tạo bình luận thành công"
    msg_update_comment_successfully = "Cập nhật bình luận thành công"
    msg_delete_comment_successfully = "Xóa bình luận thành công"
    msg_payment_required="Cuộc hẹn này yêu cầu bạn thanh toán trước khi xác nhận đặt lịch. Vui lòng thực hiện thanh toán để hoàn tất quá trình đặt hẹn."
    msg_payment_error = "Hệ thống thanh toán hiện tại đang gặp sự cố, vui lòng thử lại sau"
    msg_payment_not_found="Không tìm thấy thông tin thanh toán"
    msg_payment_fail = "Thanh toán thất bại, nêu bạn chắc chắn đã thanh toán thành công  xin vui lòng liên hệ với chúng tôi đễ hỗ trợ!!!"
    msg_patient_not_found = "Không tìm thấy thông tin bệnh nhân"
    msg_conflict_working_schedule_with_appointment = "Phát hiện có cuộc hẹn đã được lên lịch vì thế bạn không thể thay đổi thời gian này !!!"

    msg_not_verify = "Bác sĩ chưa được xác minh, vui lòng chờ xác minh từ quản trị viên"
    msg_not_found_appointment_for_conversation = "Không tìm thấy cuộc hẹn hoặc bạn không được phép tạo cuộc trò chuyện trong cuộc hẹn này"

class MsgEnumBase(Enum):
    DES_MEDIA_FILE: Final[str] = "is video of post, and accept one file"
    DES_POST_CONTENT: Final[str] = "content of post"
    DES_POST_EXAMPLE: Final[str] = "How to clean your skin"

    MSG_CREATE_WORK_SCHEDULE_SUCCESSFULLY: Final[str] = "Bạn đã tạo lịch làm việc thành công"
    CONFLICT_SCHEDULE_EXAMINATION_TYPE: Final[str] = (
        "Lịch làm việc bị xung đột với loại lịch làm việc khác, bạn vui lòng kiêm tra lại"
    )
    REJECT_DOCTOR_SUCCESSFULLY: Final[str] = (
        "Bạn đã từ chối bác sĩ này tham gia vào hệ thống khám bệnh  thành công"
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
