from sqlalchemy import inspect, text
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
from app.database.db_globals import engine

# Определяем базовый класс
Base = declarative_base()

load_dotenv()

def run_migration_schedule():
    # Подключение к базе данных
    #engine = create_engine(DATABASE_URL, echo=True)

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
        
        # Добавляем столбец schedule_type, если его нет
    if 'schedule_type' not in columns:
        try:
            with engine.begin() as connection:
                connection.execute(text('ALTER TABLE schedule ADD COLUMN schedule_type VARCHAR;'))
            print('Столбец schedule_type успешно добавлен.')
        except Exception as e:
            print(f'Ошибка при добавлении столбца schedule_type: {e}')
    else:
        print('Столбец schedule_type уже существует.')
        

#if __name__ == '__main__':
 #   run_migration()