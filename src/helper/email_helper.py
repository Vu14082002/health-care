# -*- send_mail_verify.py: Email verification task -*-

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.config import config

HTML_HEADER = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Password Reset Request</title>
</head>
"""


async def send_mail_password(email: str, token: str) -> str:
    _subject = "Yêu cầu đặt lại mật khẩu đăng nhập Health Care System"
    _to_mail = email
    link_token = config.LINK_VERIFY_EMAIL + "?token=" + token

    HTML_BODY = f"""
<body>
    <table border="0" cellpadding="" cellspacing="0" style="
                        padding-top: 16px;
                        background-color: #ffffff;
                        font-family: Calibri, Arial, sans-serif;
                        font-size: 11px;
                        color: #454748;
                        width: 100%;
                        border-collapse: separate;
                    ">
        <thead>
            <tr style="margin-bottom: 16px; display: block;">
                <td>
                    <img src="https://rubee.com.vn/wp-content/uploads/2021/05/Logo-IUH.jpg" alt="Logo  health care" style='width: 20%;' />
                </td>
            </tr>
        </thead>
        <tbody style='margin-top: 10x;'>
            <tr style="margin-bottom: 16px; display: block;">
                <td><span style='margin-top: 10px;'>Thân chào bạn</span></td>
            </tr>
            <tr>
                <td>
                    <p>
                        Chúng tôi vừa nhận được yêu cầu đặt lại mật khẩu cho tài khoản của bạn, vui lòng bấm vào liên kết
                        sau để đặt lại mật khẩu: <a style="color:#333" href="{link_token}">[Liên kết]</a>
                    </p>
                    <p>
                        Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua thư này.
                    </p>
                    <p>
                        Để bảo mật tài khoản, bạn vui lòng không chia sẻ liên kết này với bất kỳ ai.
                    </p>
                </td>
            </tr>
        </tbody>
        <tfoot style='margin-top: 10x;'>
            <tr style="margin-bottom: 16px; display: block;">
                <td>
                    <p>Cảm ơn bạn đã sử dụng dịch vụ của chúng tôi.</p>
                    <td>
                        <p>Trân trọng,</p>
                        <p>Đội ngũ Health Care System.</p>
                    </td>
                </td>
            </tr>
            <tr>
                <td>
                    <p>
                        LƯU Ý: Thư điện tử này là bảo mật và có thể đã đăng ký bảo mật về pháp lý. Trong trường hợp Quý
                        khách không phải là người nhận thư, vui lòng không sao chép, chuyển tiếp, tiết lộ hoặc sử dụng bất
                        kỳ nội dung nào trong thư điện tử này. Nếu Quý khách nhận được thông tin này do nhầm lẫn, vui lòng
                        xóa bỏ email này và tất cả các bản sao khỏi hệ thống của Quý khách và thông báo ngay cho người gửi.
                    </p>
                    <p>
                        DISCLAIMER: This e-mail is confidential. It may also be legally privileged. If you are not the
                        addressee you may not copy, forward, disclose or use any part of it. If you have received this
                        message in error, please delete it and all copies from your system and notify the sender immediately
                        by return e-mail.
                    </p>
                </td>
            </tr>
        </tfoot>
    </table>
</body>

</html>

    """
    html_content = HTML_HEADER + HTML_BODY
    mail = smtplib.SMTP_SSL(config.SMTP_HOST, config.SMTP_PORT)
    mail.login(config.SMTP_MAIL, config.SMTP_PASSWORD)
    message = MIMEMultipart("alternative")
    message["Subject"] = _subject
    message["From"] = config.SMTP_USERNAME
    message["To"] = _to_mail
    mime_html = MIMEText(html_content, "html")
    message.attach(mime_html)
    mail.sendmail(config.SMTP_USERNAME, _to_mail, message.as_string())
    mail.quit()
    return "success"


async def send_mail_register_success(email: str, *args, **kwargs) -> str:
    _subject = "Chúc mừng! Bạn đã đăng ký tài khoản Health Care System thành công"
    _to_mail = email

    HTML_BODY = """
<body>
    <table border="0" cellpadding="0" cellspacing="0" style="
                        padding-top: 16px;
                        background-color: #ffffff;
                        font-family: Calibri, Arial, sans-serif;
                        font-size: 11px;
                        color: #454748;
                        width: 100%;
                        border-collapse: separate;
                    ">
        <thead>
            <tr style="margin-bottom: 16px; display: block;">
                <td>
                    <img src="https://rubee.com.vn/wp-content/uploads/2021/05/Logo-IUH.jpg" alt="Logo health care" style='width: 20%;' />
                </td>
            </tr>
        </thead>
        <tbody style='margin-top: 10px;'>
            <tr style="margin-bottom: 16px; display: block;">
                <td><span style='margin-top: 10px;'>Xin chào,</span></td>
            </tr>
            <tr>
                <td>
                    <p>
                        Chúc mừng bạn đã đăng ký tài khoản thành công vào hệ thống Health Care System!
                    </p>
                    <p>
                        Nếu bạn không thực hiện đăng ký này, vui lòng bỏ qua email này.
                    </p>
                    <p>
                        Cảm ơn bạn đã lựa chọn Health Care System để chăm sóc sức khỏe của mình.
                    </p>
                </td>
            </tr>
        </tbody>
        <tfoot style='margin-top: 10px;'>
            <tr style="margin-bottom: 16px; display: block;">
                <td>
                    <p>Cảm ơn bạn đã sử dụng dịch vụ của chúng tôi.</p>
                    <td>
                        <p>Trân trọng,</p>
                        <p>Đội ngũ Health Care System.</p>
                    </td>
                </td>
            </tr>
            <tr>
                <td>
                    <p>
                        LƯU Ý: Thư điện tử này là bảo mật và có thể đã đăng ký bảo mật về pháp lý. Trong trường hợp bạn không phải là người nhận thư, vui lòng không sao chép, chuyển tiếp, tiết lộ hoặc sử dụng bất kỳ nội dung nào trong thư điện tử này. Nếu bạn nhận được email này do nhầm lẫn, vui lòng xóa bỏ email này và thông báo ngay cho người gửi.
                    </p>
                </td>
            </tr>
        </tfoot>
    </table>
</body>
</html>
    """
    html_content = HTML_HEADER + HTML_BODY
    mail = smtplib.SMTP_SSL(config.SMTP_HOST, config.SMTP_PORT)
    mail.login(config.SMTP_MAIL, config.SMTP_PASSWORD)
    message = MIMEMultipart("alternative")
    message["Subject"] = _subject
    message["From"] = config.SMTP_USERNAME
    message["To"] = _to_mail
    mime_html = MIMEText(html_content, "html")
    message.attach(mime_html)
    mail.sendmail(config.SMTP_USERNAME, _to_mail, message.as_string())
    mail.quit()
    return "success"
