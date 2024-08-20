from typing import TYPE_CHECKING  # type: ignore
from uuid import uuid4

from sqlalchemy import UUID, Column, ForeignKey, Integer, String, Text, event
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.postgresql import Model


class DermatologyMedicalRecords(Model):
    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
