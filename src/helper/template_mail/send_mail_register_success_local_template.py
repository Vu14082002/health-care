def send_mail_register_success_local_template(phone_number: str, password: str) -> str:
    HTML_BODY = f"""
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
                                Admin đã thêm bạn vào hệ thống Health Care System với vai trò là bác sĩ.
                            </p>
                            <p>
                                Thông tin tài khoản của bạn như sau:
                            </p>
                            <ul>
                                <li><strong>Số điện thoại:</strong> {phone_number}</li>
                                <li><strong>Mật khẩu:</strong> {password}</li>
                            </ul>
                            <p>
                                Nếu bạn không yêu cầu thêm tài khoản này, vui lòng bỏ qua email này.
                            </p>
                            <p>
                                Để bắt đầu, hãy đăng nhập vào tài khoản của bạn và cập nhật thông tin cá nhân nếu cần thiết.
                            </p>
                            <p>
                                Nếu bạn có bất kỳ câu hỏi nào, hãy liên hệ với đội ngũ hỗ trợ của chúng tôi qua email: support@healthcaresystem.vn hoặc số điện thoại: 0123 456 789.
                            </p>
                            <p>
                                Cảm ơn bạn đã tham gia vào hệ thống chăm sóc sức khỏe của chúng tôi.
                            </p>
                        </td>
                    </tr>
                </tbody>
                <tfoot style='margin-top: 10px;'>
                    <tr style="margin-bottom: 16px; display: block;">
                        <td>
                            <p>Cảm ơn bạn một lần nữa.</p>
                            <p>Trân trọng,</p>
                            <p>Đội ngũ tuyển dụng</p>
                            <p>**Health Care System**</p>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <p>
                                **Lưu ý: Vui lòng không trả lời email này. Email này được gửi từ hộp thư không được giám sát. Các phản hồi sẽ không được đọc.**
                            </p>
                        </td>
                    </tr>
                </tfoot>
            </table>
        </body>
    """

    return HTML_BODY
