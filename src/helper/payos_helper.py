import random
from datetime import datetime, timedelta

import pytz
from payos import PaymentData
from payos.type import PaymentLinkInformation

from src.config import payOsIns


class PaymentHelper:
    def __init__(self):
        pass

    def create_payment(
        self,
        amount: int,
        description: str,
        returnUrl: str,
        cancelUrl:str = "",
        time_session:int = 300
    ):
        try:
            # utc_plus_7 = pytz.timezone("Asia/Ho_Chi_Minh")
            # current_time_utc = datetime.now(pytz.utc)
            # current_time_utc_plus_7 = current_time_utc.astimezone(utc_plus_7)
            # time_expired = current_time_utc_plus_7 + timedelta(seconds=time_session)
            # expired_at = int(time_expired.timestamp())
            # random_number= random.randint(1000, 99999)
            # payment_data = PaymentData(
            #     orderCode=random_number,
            #     amount=amount,
            #     description=description,
            #     cancelUrl=cancelUrl,
            #     returnUrl=returnUrl,
            #     expiredAt=expired_at,
            # )
            # payOsCreatePayment = payOsIns.createPaymentLink( payment_data)
            # payOsCreatePayment = payOsCreatePayment.to_json()
            # return payOsCreatePayment
            return "xinchao"
        except Exception as e:
            print(e)
            return None

    def get_payment_info(
        self,
        orderId: str
    ):
        try:
            paymentLinkInfo: PaymentLinkInformation = payOsIns.getPaymentLinkInformation(orderId = orderId)
            return paymentLinkInfo.to_json()

        except Exception as e:
            print(e)
            return None
