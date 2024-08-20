from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database.postgresql import Model


class InventoryModel(Model):
    __tablename__ = "inventory"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)

    item_name: Mapped[str] = mapped_column(String(255), nullable=False)

    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    expiration_date: Mapped[str] = mapped_column(Date, nullable=True)

    def __repr__(self):
        return f"<Inventory(id={self.id}, item_name='{self.item_name}', quantity={self.quantity})>"
