import logging
from app.models import Schedule  
from app.database.db_globals import Session
import logging 

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class ScheduleManager():
    def __init__(self):
        logging.debug("ScheduleManager инициализирован.")
        self.Session = Session
        if Session is None:
            print("Session in ScheduleManager is None!")
        else:
            print("Session found successfully!")

   # Методы для работы с таблицей Schedule
    def add_schedule(self, method, url, data=None, interval=None, last_run=None, schedule_type='interval', time_of_day=None):
        logging.debug("add_schedule вызывается.")
        session = self.Session()  # Открываем сессию
        logging.debug("Session успешно получена.")
        try:
            # Проверяем, что параметры корректны в зависимости от типа расписания
            if schedule_type == 'interval' and not interval:
                raise ValueError("Interval is required for 'interval' schedule type.")
            if schedule_type == 'daily' and not time_of_day:
                raise ValueError("Time of day is required for 'daily' schedule type.")
            
            # Создаем объект Schedule
            new_schedule = Schedule(
                method=method,
                url=url,
                data=data,
                interval=interval,
                last_run=last_run,
                schedule_type=schedule_type,
                time_of_day=time_of_day
            )
            
            # Добавляем объект в сессию
            session.add(new_schedule)

            # Привязываем объект к сессии и выполняем commit
            session.commit()

            # После commit объект привязан к сессии, и мы можем к нему обращаться
            logging.info(f"Schedule added to DB with ID: {new_schedule.id}")
            
            return new_schedule

        except Exception as e:
            session.rollback()  # Откат транзакции при ошибке
            logging.error(f"Failed to add schedule to DB: {e}")
            return None

        finally:
            session.close()  # Закрываем сессию после всех операций

    def update_schedule(self, schedule):
        """
        Обновляет запись в таблице schedule.
        """
        logging.debug("update_schedule вызывается.")
        session = self.Session()
        try:
            # Сохраняем изменения в объекте расписания
            session.merge(schedule)  # Метод merge добавляет или обновляет объект
            session.commit()
        except Exception as e:
            session.rollback()  # Откат транзакции в случае ошибки
        finally:
            session.close()

    def deactivate_schedule(self, schedule_id):
        """Деактивация записи из таблицы Schedule по id"""
        logging.debug("deactivate_schedule вызывается.")
        session = self.Session()
        try:
            schedule = session.query(Schedule).filter_by(id=schedule_id).first()

            if schedule:
                # Деактивация расписания
                schedule.is_active = False
                session.commit()
                
                return True
            else:
                
                return False
        except Exception as e:
            session.rollback()
            
            return False
        finally:
            session.close()

    def get_active_schedules(self):
        """Получить все активные расписания"""
        logging.debug("get_active_schedules вызывается.")
        session = self.Session()
        try:
            schedules = session.query(Schedule).filter_by(is_active=True).all()
            return schedules
        finally:
            session.close()


    def schedule_exists(self, schedule_id):
        """Проверка существования расписания по id"""
        logging.debug("schedule_exists вызывается.")
        session = self.Session()
        exists_query = session.query(Schedule).filter_by(id=schedule_id).first() is not None
        session.close()
        return exists_query

    def get_all_schedules(self):
        """Получить все расписания (активные и неактивные)"""
        logging.debug("get_all_schedules вызывается.")
        session = self.Session()
        try:
            schedules = session.query(Schedule).all()
            return schedules
        finally:
            session.close()

    def get_schedule_by_id(self, schedule_id):
        """Получить конкретное расписание по id"""
        logging.debug("get_schedule_by_id вызывается.")
        session = self.Session()
        try:
            # Получаем расписание по id
            schedule = session.query(Schedule).filter_by(id=schedule_id).first()
        finally:
            # Закрываем сессию в блоке finally, чтобы гарантировать закрытие независимо от результата запроса
            session.close()

        # Возвращаем найденное расписание или None, если не найдено
        return schedule
