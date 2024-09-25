"""remove filed timestamp in notification

Revision ID: eb50dccf9282
Revises: b03c6e4d2d2b
Create Date: 2024-09-21 10:05:19.800475

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'eb50dccf9282'
down_revision: Union[str, None] = 'b03c6e4d2d2b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('notification', 'timestamp')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('notification', sa.Column('timestamp', postgresql.TIMESTAMP(), autoincrement=False, nullable=False))
    # ### end Alembic commands ###