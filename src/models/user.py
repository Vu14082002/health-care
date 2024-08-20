from datetime import datetime, timezone
from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.postgresql import Model
from src.models.user_roles import UserRolesModel

if TYPE_CHECKING:
    from src.models.patient import PatientModel
    from src.models.role import RoleModel
    from src.models.user_roles import UserRolesModel
else:
    PatientModel = "PatientModel"
    RoleModel = "RoleModel"
    UserRolesModel = "UserRolesModel"


def get_current_time() -> int:
    """Returns the current UTC timestamp as an integer."""
    return int(datetime.now(timezone.utc).timestamp())


class UserModel(Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(
        name="id",
        type_=Integer,
        primary_key=True,
        autoincrement=True
    )

    phone: Mapped[str] = mapped_column(
        name="username",
        type_=String,
        nullable=False,
        unique=True
    )

    password: Mapped[str] = mapped_column(
        name="password",
        type_=String,
        nullable=False
    )

    roles: Mapped[List["RoleModel"]] = relationship(
        "RoleModel",
        secondary="user_roles",
        back_populates="users",
        uselist=True,
        lazy="joined"
    )

    user_roles: Mapped[List["UserRolesModel"]] = relationship(
        "UserRolesModel",
        back_populates="user"
    )

    patient: Mapped["PatientModel"] = relationship(
        "PatientModel",
        back_populates="user",
        uselist=False,
        lazy="joined"
    )
