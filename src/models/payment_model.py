import enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.postgresql import Model

if TYPE_CHECKING:
    from src.models.appointment_model import AppointmentModel


class PaymentMethod(enum.Enum):
    CASH = "cash"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"
    GOOGLE_PAY = "google_pay"
    APPLE_PAY = "apple_pay"
    SAMSUNG_PAY = "samsung_pay"
    OTHER = "other"


class PaymentModel(Model):
    __tablename__ = "payment"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)

    appointment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('appointment.id'), nullable=False)

    amount: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False)

    payment_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    payment_method: Mapped[str] = mapped_column(
        String, nullable=False, default=PaymentMethod.CASH.value)

    appointment: Mapped["AppointmentModel"] = relationship(
        "AppointmentModel", back_populates="payment"
    )

    def __repr__(self):
        return f"<Payment(id={self.id}, appointment_id={self.appointment_id}, amount={self.amount}, payment_time={self.payment_time})>"
