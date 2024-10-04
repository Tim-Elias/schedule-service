"""Initial migration

Revision ID: 19313f2f3f9c
Revises: 
Create Date: 2024-10-04 13:33:36.651641

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '19313f2f3f9c'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    op.drop_table('request_log')
    op.drop_table('schedule')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('schedule',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('schedule_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('method', sa.VARCHAR(length=10), autoincrement=False, nullable=False),
    sa.Column('url', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('data', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('interval', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('time_of_day', postgresql.TIME(), autoincrement=False, nullable=True),
    sa.Column('schedule_type', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('last_run', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='schedule_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_table('request_log',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('schedule_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('response', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('timestamp', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['schedule_id'], ['schedule.id'], name='request_log_schedule_id_fkey', ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name='request_log_pkey')
    )
    op.create_table('users',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('password_hash', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('google_id', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('auth_type', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='users_pkey'),
    sa.UniqueConstraint('google_id', name='users_google_id_key'),
    sa.UniqueConstraint('user_id', name='users_user_id_key')
    )
    # ### end Alembic commands ###
