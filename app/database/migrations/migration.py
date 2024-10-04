from app.database.migrations.password import admin
#from app.database.migrations.migration_schedule import run_migration_schedule
#from app.database.migrations.migration_users import run_migration_users


def migrate(app):
    password=app.config['PASSWORD']
    login=app.config['LOGIN']
    admin(password, login)
    #run_migration_schedule()
    #run_migration_users()
    