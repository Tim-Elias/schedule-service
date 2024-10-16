"""Alter schedule_id in request_log

Revision ID: 7e7093f3199c
Revises: 5b7966246c56
Create Date: 2024-10-10 18:27:00.323653

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7e7093f3199c'
down_revision: Union[str, None] = '5b7966246c56'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Изменяем тип schedule_id и добавляем ondelete='CASCADE'
    op.alter_column(
        'request_log',  # имя таблицы
        'schedule_id',  # имя столбца
        type_=sa.String(36),  # новый тип
        existing_type=sa.Integer(),  # старый тип
        postgresql_using='schedule_id::text',  # кастомное преобразование для PostgreSQL (если используется)
        nullable=True  # оставляем nullable
    )
    op.create_foreign_key(
        'fk_request_log_schedule',  # имя внешнего ключа
        'request_log',  # имя таблицы, в которой создается внешний ключ
        'schedule',  # имя таблицы, на которую ссылается внешний ключ
        ['schedule_id'],  # имя поля во внешнем ключе
        ['id'],  # имя поля, на которое ссылается внешний ключ
        ondelete='CASCADE'  # каскадное удаление
    )


def downgrade():
    # Возвращаем изменения, если нужно
    op.drop_constraint('fk_request_log_schedule', 'request_log', type_='foreignkey')
    op.alter_column(
        'request_log',  # имя таблицы
        'schedule_id',  # имя столбца
        type_=sa.Integer(),  # возвращаем старый тип
        existing_type=sa.String(36),  # новый тип
        nullable=True  # оставляем nullable
    )