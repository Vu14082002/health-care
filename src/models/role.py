from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.postgresql import Model

if TYPE_CHECKING:
    from src.models import UserModel, UserRolesModel
else:
    UserModel = "UserModel"
    UserRolesModel = "UserRolesModel"


class EnumRole(str, Enum):
    ADMIN = "admin"
    PROFESSIONAL = "professional"
    DOCTOR = "doctor"
    NURSE = "nurse"
    PATIENT = "patient"


class RoleModel(Model):
    __tablename__ = "role"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True
    )

    description: Mapped[str] = mapped_column(
        String,
        default=""
    )

    users: Mapped[List["UserModel"]] = relationship(
        "UserModel",
        secondary="user_roles",
        back_populates="roles"
    )

    user_roles: Mapped[List["UserRolesModel"]] = relationship(
        "UserRolesModel",
        back_populates="role"
    )
