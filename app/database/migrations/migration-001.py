from sqlalchemy import create_engine, Column, Time
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
import os
from dotenv import load_dotenv

# Определяем базовый класс
Base = declarative_base()

load_dotenv()

def run_migration():
    # Подключение к базе данных
    DATABASE_URL = os.getenv('DATABASE_URL')
    engine = create_engine(DATABASE_URL, echo=True)
    connection = engine.connect()

    # Проверяем, существует ли столбец
    from sqlalchemy import inspect
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns('schedule')]

    if 'time_of_day' not in columns:
        # Выполняем SQL-команду для добавления столбца
        try:
            connection.execute(text('ALTER TABLE schedule ADD COLUMN time_of_day TIME;'))
            print('Столбец time_of_day успешно добавлен.')
        except Exception as e:
            print(f'Ошибка при добавлении столбца: {e}')
    else:
        print('Столбец time_of_day уже существует.')

    connection.close()

if __name__ == '__main__':
    run_migration()