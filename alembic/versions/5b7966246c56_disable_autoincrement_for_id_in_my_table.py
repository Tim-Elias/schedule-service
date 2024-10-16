from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5b7966246c56'
down_revision = 'cd81b5f32c05'
branch_labels = None
depends_on = None


def upgrade():
    # Удаляем внешнее ключевое ограничение
    op.drop_constraint('request_log_schedule_id_fkey', 'request_log', type_='foreignkey')

    # Изменяем тип 'id' на String в таблице 'users'
    op.alter_column('users', 'id', existing_type=sa.Integer(), type_=sa.String(36))

    # Изменяем тип 'id' на String в таблице 'schedule'
    op.alter_column('schedule', 'id', existing_type=sa.Integer(), type_=sa.String(36))

    # Изменяем тип 'id' на String в таблице 'request_log'
    op.alter_column('request_log', 'id', existing_type=sa.Integer(), type_=sa.String(36))

    # Изменяем тип столбца 'schedule_id' на String
    op.alter_column('request_log', 'schedule_id', existing_type=sa.Integer(), type_=sa.String(36))

    # Повторно создаем ограничение внешнего ключа
    op.create_foreign_key('request_log_schedule_id_fkey', 'request_log', 'schedule', ['schedule_id'], ['id'], ondelete='SET NULL')


def downgrade():
    # Удаляем внешнее ключевое ограничение
    op.drop_constraint('request_log_schedule_id_fkey', 'request_log', type_='foreignkey')

    # Восстанавливаем тип 'id' обратно в Integer в таблице 'users'
    op.alter_column('users', 'id', existing_type=sa.String(36), type_=sa.Integer())

    # Восстанавливаем тип 'id' обратно в Integer в таблице 'schedule'
    op.alter_column('schedule', 'id', existing_type=sa.String(36), type_=sa.Integer())

    # Восстанавливаем тип 'id' обратно в Integer в таблице 'request_log'
    op.alter_column('request_log', 'id', existing_type=sa.String(36), type_=sa.Integer())

    # Восстанавливаем тип 'schedule_id' обратно в Integer
    op.alter_column('request_log', 'schedule_id', existing_type=sa.String(36), type_=sa.Integer())

    # Повторно создаем ограничение внешнего ключа
    op.create_foreign_key('request_log_schedule_id_fkey', 'request_log', 'schedule', ['schedule_id'], ['id'], ondelete='SET NULL')
