from typing import TYPE_CHECKING

from sqlalchemy import DECIMAL, Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.postgresql import Model

if TYPE_CHECKING:
    from models.patient import PatientModel
else:
    PatientModel = "PatientModel"


class BillingModel(Model):
    __tablename__ = "bill"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)

    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patient.id"), nullable=False)

    amount: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)

    billing_date: Mapped[str] = mapped_column(Date, nullable=False)

    payment_status: Mapped[str] = mapped_column(String(50), nullable=False)

    patient: Mapped["PatientModel"] = relationship(
        "PatientModel", back_populates="billings")

    def __repr__(self):
        return f"<Billing(id={self.id}, patient_id={self.patient_id}, amount={self.amount}, billing_date='{self.billing_date}')>"
