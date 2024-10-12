from src.helper.template_mail.reject_template import send_mail_reject_register
from src.helper.template_mail.send_mail_password_template import (
    send_mail_password_change_template,
)
from src.helper.template_mail.send_mail_register_foreign_template import (
    send_mail_register_success_foreign_template,
)
from src.helper.template_mail.send_mail_register_success_local_template import (
    send_mail_register_success_local_template,
)
from src.helper.template_mail.send_mail_request_additional_info_template import (
    send_mail_request_additional_info_template,
)

__all__ = [
    "send_mail_reject_register",
    "send_mail_password_change_template",
    "send_mail_register_success_local_template",
    "send_mail_register_success_foreign_template",
    "send_mail_request_additional_info_template",
]
