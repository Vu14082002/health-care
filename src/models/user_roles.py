from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.postgresql import Model

if TYPE_CHECKING:
    from src.models.role import RoleModel
    from src.models.user import UserModel
else:
    RoleModel = "RoleModel"
    UserModel = "UserModel"


class UserRolesModel(Model):
    __tablename__ = "user_roles"

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('user.id', ondelete='CASCADE'),
        primary_key=True
    )
    role_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('role.id', ondelete='CASCADE'),
        primary_key=True
    )

    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="user_roles"
    )

    role: Mapped["RoleModel"] = relationship(
        "RoleModel",
        back_populates="user_roles"
    )
