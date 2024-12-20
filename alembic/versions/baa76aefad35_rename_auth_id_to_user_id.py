"""rename auth_id to user_id

Revision ID: baa76aefad35
Revises: ce4ffed02ba3
Create Date: 2024-10-13 11:43:32.682142

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'baa76aefad35'
down_revision: Union[str, None] = 'ce4ffed02ba3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comment', sa.Column('user_id', sa.Integer(), nullable=False))
    op.drop_index('ix_comment_author_post', table_name='comment')
    op.create_index('ix_comment_user_post', 'comment', ['user_id', 'post_id'], unique=False)
    op.drop_constraint('comment_author_id_fkey', 'comment', type_='foreignkey')
    op.create_foreign_key(None, 'comment', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_column('comment', 'author_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comment', sa.Column('author_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'comment', type_='foreignkey')
    op.create_foreign_key('comment_author_id_fkey', 'comment', 'user', ['author_id'], ['id'], ondelete='CASCADE')
    op.drop_index('ix_comment_user_post', table_name='comment')
    op.create_index('ix_comment_author_post', 'comment', ['author_id', 'post_id'], unique=False)
    op.drop_column('comment', 'user_id')
    # ### end Alembic commands ###
