def send_mail_request_final_success() -> str:
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
                        <img src="https://rubee.com.vn/wp-content/uploads/2021/05/Logo-IUH.jpg" alt="Logo Health Care" style='width: 20%;' />
                    </td>
                </tr>
            </thead>
            <tbody style='margin-top: 10px;'>
                <tr style="margin-bottom: 16px; display: block;">
                    <td><span style='margin-top: 10px;'>Kính gửi Vũ,</span></td>
                </tr>
                <tr>
                    <td>
                        <p>
                            Cảm ơn bạn đã bày tỏ sự quan tâm đến vị trí Bác sĩ tại **Health Care System**.
                        </p>
                        <p>
                            Chúng tôi vui mừng thông báo rằng sau khi quản trị viên đã xác minh hồ sơ của bạn lần thứ hai, bạn đã được phê duyệt. Bạn có thể ngay lập tức truy cập vào hệ thống của chúng tôi và tiếp tục thực hiện đăng nhập bằng số điện thoại bạn đã cung cấp khi đăng ký.
                        </p>
                        <p>
                            Chúng tôi rất mong nhận được phản hồi từ bạn để hoàn tất các thủ tục tiếp theo.
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
                <tr>
                    <td>
                        <p>
                            LƯU Ý: Thư điện tử này là bảo mật và có thể đã đăng ký bảo mật về pháp lý. Trong trường hợp Quý khách không phải là người nhận thư, vui lòng không sao chép, chuyển tiếp, tiết lộ hoặc sử dụng bất kỳ nội dung nào trong thư điện tử này. Nếu Quý khách nhận được thông tin này do nhầm lẫn, vui lòng xóa bỏ email này và tất cả các bản sao khỏi hệ thống của Quý khách và thông báo ngay cho người gửi.
                        </p>
                        <p>
                            DISCLAIMER: This e-mail is confidential. It may also be legally privileged. If you are not the addressee, you may not copy, forward, disclose, or use any part of it. If you have received this message in error, please delete it and all copies from your system and notify the sender immediately by return e-mail.
                        </p>
                    </td>
                </tr>
            </tfoot>
        </table>
    </body>
    </html>
    """
    return HTML_BODY
