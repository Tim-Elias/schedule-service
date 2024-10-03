from password import admin
from migration_schedule import run_migration_schedule
from migration_users import run_migration_users


def migrate(app):
    password=app.config['PASSWORD']
    login=app.config['LOGIN']
    admin(password, login)
    run_migration_schedule()
    run_migration_users()
    