def send_mail_reject_register() -> str:
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
                            Sau khi xem xét hồ sơ của bạn, chúng tôi rất tiếc phải thông báo rằng kinh nghiệm và nền tảng của bạn không hoàn toàn phù hợp với yêu cầu của vị trí này, và vì vậy chúng tôi sẽ không tiếp tục với đơn ứng tuyển của bạn. Xin lưu ý rằng điều này không phản ánh sự thiếu đánh giá đối với kỹ năng và khả năng của bạn.
                        </p>
                        <p>
                            Chúng tôi khuyến khích bạn tiếp tục khám phá các cơ hội nghề nghiệp khác với chúng tôi và kiểm tra các vị trí tuyển dụng khác khi chúng tôi tiếp tục phát triển. Hãy theo dõi chúng tôi trên <a href="https://www.linkedin.com/company/health-care-system" target="_blank">LinkedIn</a> để cập nhật thông tin về các vị trí tuyển dụng và tin tức.
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
