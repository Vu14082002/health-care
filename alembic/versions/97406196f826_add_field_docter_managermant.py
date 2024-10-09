"""add field: docter managermant

Revision ID: 97406196f826
Revises: 2e8040defe4d
Create Date: 2024-09-19 17:35:34.411856

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '97406196f826'
down_revision: Union[str, None] = '2e8040defe4d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
