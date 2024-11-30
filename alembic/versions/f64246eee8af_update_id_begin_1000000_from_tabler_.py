"""update id begin 1000000 from tabler appointment

Revision ID: f64246eee8af
Revises: 14dbc03d44c5
Create Date: 2024-12-01 01:19:00.075556

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f64246eee8af'
down_revision: Union[str, None] = '14dbc03d44c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Đảm bảo sequence đang được sử dụng cho cột 'id' bắt đầu từ 1000000
    # Lệnh này sẽ thay đổi giá trị bắt đầu của sequence cho bảng appointment
    op.execute("""
        ALTER SEQUENCE appointment_id_seq RESTART WITH 1000000;
    """)

def downgrade() -> None:
    # Trở lại giá trị ban đầu (hoặc một giá trị khác tùy theo yêu cầu của bạn)
    op.execute("""
        ALTER SEQUENCE appointment_id_seq RESTART WITH 1;
    """)
