"""remove rep_id

Revision ID: 14dbc03d44c5
Revises: 4242073f236d
Create Date: 2024-10-30 00:05:45.889934

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '14dbc03d44c5'
down_revision: Union[str, None] = '4242073f236d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('comment_rep_id_fkey', 'comment', type_='foreignkey')
    op.drop_column('comment', 'rep_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comment', sa.Column('rep_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('comment_rep_id_fkey', 'comment', 'comment', ['rep_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###