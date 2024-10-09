"""add field name appointment

Revision ID: 9dbe3d0a3cd8
Revises: 21a5aa60121f
Create Date: 2024-10-10 00:30:05.024799

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9dbe3d0a3cd8'
down_revision: Union[str, None] = '21a5aa60121f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('appointment', sa.Column('name', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('appointment', 'name')
    # ### end Alembic commands ###
