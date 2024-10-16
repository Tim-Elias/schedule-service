"""Add status_code to request_log table

Revision ID: 351d9f441d34
Revises: 7e7093f3199c
Create Date: 2024-10-14 15:31:34.384005

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '351d9f441d34'
down_revision: Union[str, None] = '7e7093f3199c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Добавляем новый столбец status_code
    op.add_column('request_log', sa.Column('status_code', sa.Integer(), nullable=True))

def downgrade():
    # Удаляем столбец status_code, если необходимо откатить миграцию
    op.drop_column('request_log', 'status_code')
