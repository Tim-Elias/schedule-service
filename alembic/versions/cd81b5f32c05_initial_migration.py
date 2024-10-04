"""Initial migration

Revision ID: cd81b5f32c05
Revises: 
Create Date: 2024-10-04 14:05:04.909931

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cd81b5f32c05'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Создаем таблицу users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.String, unique=True, nullable=False),
        sa.Column('password_hash', sa.String, nullable=True),
        sa.Column('google_id', sa.String, unique=True, nullable=True),
        sa.Column('auth_type', sa.String, nullable=False, default='password')
    )

    # Создаем таблицу schedule
    op.create_table(
        'schedule',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('method', sa.String(10), nullable=False),
        sa.Column('url', sa.String(255), nullable=False),
        sa.Column('data', sa.Text, nullable=True),
        sa.Column('interval', sa.Integer, nullable=True),
        sa.Column('time_of_day', sa.Time, nullable=True),
        sa.Column('schedule_type', sa.String(50), nullable=False, default='interval'),
        sa.Column('last_run', sa.DateTime, nullable=True),
        sa.Column('is_active', sa.Boolean, default=True)
    )

    # Создаем таблицу request_log
    op.create_table(
        'request_log',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('schedule_id', sa.Integer, sa.ForeignKey('schedule.id', ondelete='SET NULL'), nullable=True),
        sa.Column('response', sa.Text, nullable=False),
        sa.Column('timestamp', sa.DateTime, nullable=False, default=sa.func.now())
    )


def downgrade() -> None:
    # Удаляем таблицу request_log
    op.drop_table('request_log')

    # Удаляем таблицу schedule
    op.drop_table('schedule')

    # Удаляем таблицу users
    op.drop_table('users')
