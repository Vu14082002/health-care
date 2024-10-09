"""add nullable for patient

Revision ID: 9726f3fde895
Revises: 353c055035be
Create Date: 2024-09-19 17:42:46.594411

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9726f3fde895'
down_revision: Union[str, None] = '353c055035be'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
