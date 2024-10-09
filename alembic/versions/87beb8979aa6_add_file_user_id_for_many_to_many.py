"""add file user_id for many to many

Revision ID: 87beb8979aa6
Revises: 6e0ed0e5261f
Create Date: 2024-09-20 15:56:21.188752

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '87beb8979aa6'
down_revision: Union[str, None] = '6e0ed0e5261f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
