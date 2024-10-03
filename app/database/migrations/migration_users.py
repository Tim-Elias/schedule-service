from sqlalchemy import inspect, text
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
from app.database.db_globals import engine

# Определяем базовый класс
Base = declarative_base()

load_dotenv()

def run_migration_users():
    # Подключение к базе данных
    #engine = create_engine(DATABASE_URL, echo=True)

    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns('users')]
       
        # Добавляем столбец schedule_type, если его нет
    if 'google_id' not in columns:
        try:
            with engine.begin() as connection:
                connection.execute(text('ALTER TABLE users ADD COLUMN google_id VARCHAR;'))
            print('Столбец google_id успешно добавлен.')
        except Exception as e:
            print(f'Ошибка при добавлении столбца google_id: {e}')
    else:
        print('Столбец google_id уже существует.')
        
        
    if 'auth_type' not in columns:
        try:
            with engine.begin() as connection:
                connection.execute(text('ALTER TABLE users ADD COLUMN auth_type VARCHAR;'))
            print('Столбец auth_type успешно добавлен.')
        except Exception as e:
            print(f'Ошибка при добавлении столбца auth_type: {e}')
    else:
        print('Столбец auth_type уже существует.')
        

#if __name__ == '__main__':
 #   run_migration()