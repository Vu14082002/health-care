from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database.postgresql import Model

if TYPE_CHECKING:
    from src.models.user_model import UserModel


class NotificationModel(Model):
    __tablename__ = "notification"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow)
    is_read: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False)

    user: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="notifications")
