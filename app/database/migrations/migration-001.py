from sqlalchemy import create_engine, Column, Time, inspect, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
import os
from dotenv import load_dotenv

# Определяем базовый класс
Base = declarative_base()

load_dotenv()

def run_migration():
    # Подключение к базе данных
    DATABASE_URL = os.getenv('DATABASE_URL')
    engine = create_engine(DATABASE_URL, echo=True)

    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns('schedule')]

    if 'time_of_day' not in columns:
        try:
            with engine.connect() as connection:
                # Начинаем транзакцию
                trans = connection.begin()
                try:
                    connection.execute(text('ALTER TABLE schedule ADD COLUMN time_of_day TIME;'))
                    # Фиксируем транзакцию
                    trans.commit()
                    print('Столбец time_of_day успешно добавлен.')
                except Exception as e:
                    # Откатываем транзакцию в случае ошибки
                    trans.rollback()
                    print(f'Ошибка при добавлении столбца: {e}')
        except Exception as e:
            print(f'Ошибка при подключении к базе данных: {e}')
    else:
        print('Столбец time_of_day уже существует.')

if __name__ == '__main__':
    run_migration()