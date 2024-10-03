from app.database.migrations.password import admin
from app.database.migrations.migration_001 import run_migration

def migrate(app):
    password=app.config['PASSWORD']
    login=app.config['LOGIN']
    admin(password, login)
    run_migration()