import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import src.helper.template_mail as template_mail
from src.config import config
from src.core.decorator.exception_decorator import catch_error_helper


async def send_mail_password_change(email: str) -> str:
    html_body = template_mail.send_mail_password_change_template()
    return await send_mail_action(email, html_body)


async def send_mail_register_success_local(email: str, phone_number:str, password:str, *args, **kwargs) -> str:
    html_body = template_mail.send_mail_register_success_local_template(phone_number, password)
    return await send_mail_action(email, html_body)


async def send_mail_register_success_foreign(email: str, *args, **kwargs) -> str:
    html_body = template_mail.send_mail_register_success_foreign_template()
    return await send_mail_action(email, html_body)


async def send_mail_reject_register(email: str, *args, **kwargs) -> str:
    html_body = template_mail.send_mail_reject_register()
    return await send_mail_action(email, html_body)


async def send_mail_request_additional_info(email: str, message: str) -> str:
    html_body = template_mail.send_mail_request_additional_info_template(message)
    return await send_mail_action(email, html_body)

async def send_mail_request_final_success(email: str) -> str:
    html_body = template_mail.send_mail_request_final_success()
    return await send_mail_action(email, html_body)


@catch_error_helper("Failed to send mail")
async def send_mail_action(email: str, HTML_BODY, subject: str | None = None):
    HTML_HEADER = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Health Care System</title>
    </head>
    """
    _subject = "Thông báo từ Health Care System" if not subject else subject
    _to_mail = email
    html_content = HTML_HEADER + HTML_BODY
    mail = smtplib.SMTP_SSL(config.SMTP_HOST, config.SMTP_PORT)
    _ = mail.login(config.SMTP_MAIL, config.SMTP_PASSWORD)
    message = MIMEMultipart("alternative")
    message["Subject"] = _subject
    message["From"] = config.SMTP_USERNAME
    message["To"] = _to_mail
    mime_html = MIMEText(html_content, "html")
    message.attach(mime_html)
    _ = mail.sendmail(config.SMTP_USERNAME, _to_mail, message.as_string())
    _ = mail.quit()
    return "success"
