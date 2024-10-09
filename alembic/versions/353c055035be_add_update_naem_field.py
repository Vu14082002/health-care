"""add update naem field

Revision ID: 353c055035be
Revises: 97406196f826
Create Date: 2024-09-19 17:39:12.325606

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '353c055035be'
down_revision: Union[str, None] = '97406196f826'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
