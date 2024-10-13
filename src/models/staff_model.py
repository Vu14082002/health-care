from datetime import date

from sqlalchemy import (
    Date,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.postgresql.repository import Model

default_avatar = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQS0iv-HzCTjY2RQ7JLiYe23Rw2Osp-n9PqUg&s"

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.user_model import UserModel


class StaffModel(Model):
    __tablename__ = "staff"
    __table_args__ = (
        Index("idx_staff_phone_number", "phone_number"),
        Index("idx_staff_email", "email"),
    )
    id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), primary_key=True)

    first_name: Mapped[str] = mapped_column(String, nullable=False)

    last_name: Mapped[str] = mapped_column(String, nullable=False)

    phone_number: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)

    gender: Mapped[str] = mapped_column(String, nullable=False, default="other")

    avatar: Mapped[str] = mapped_column(Text, nullable=True, default=default_avatar)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    email: Mapped[str] = mapped_column(String, nullable=True, unique=True)

    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="staff",
        lazy="joined",
    )

    account_number: Mapped[str | None] = mapped_column(Text, nullable=True)

    bank_name: Mapped[str | None] = mapped_column(Text, nullable=True)

    beneficiary_name: Mapped[str | None] = mapped_column(Text, nullable=True)

    branch_name: Mapped[str | None] = mapped_column(Text, nullable=True)
