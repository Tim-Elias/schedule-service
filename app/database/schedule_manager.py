import logging
from sqlalchemy import asc, desc
from app.models import Schedule  
from app.database.db_globals import Session
import uuid
import logging 
import json

# Настройка логирования
app_logger = logging.getLogger('app_logger')

class ScheduleManager():
    def __init__(self):
        self.Session = Session

   # Методы для работы с таблицей Schedule
    def add_schedule(self, method, url, data=None, interval=None, last_run=None, schedule_type='interval', time_of_day=None):
        app_logger.debug("add_schedule вызывается.")
        session = self.Session()  # Открываем сессию
        app_logger.debug("Session успешно получена.")
        try:
            # Проверяем, что параметры корректны в зависимости от типа расписания
            if schedule_type == 'interval' and not interval:
                raise ValueError("Interval is required for 'interval' schedule type.")
            if schedule_type == 'daily' and not time_of_day:
                raise ValueError("Time of day is required for 'daily' schedule type.")
            id = str(uuid.uuid4())
            # Создаем объект Schedule
            new_schedule = Schedule(
                id = id, 
                method = method,
                url = url,
                data = json.dumps(data),
                interval = interval,
                last_run = last_run,
                schedule_type = schedule_type,
                time_of_day = time_of_day
            )
            
            # Добавляем объект в сессию
            session.add(new_schedule)
            # Привязываем объект к сессии и выполняем commit
            session.commit()
            # После commit объект привязан к сессии, и мы можем к нему обращаться
            app_logger.info(f"Schedule added to DB with ID: {new_schedule.id}")
    
            return new_schedule.to_dict()

        except Exception as e:
            session.rollback()  # Откат транзакции при ошибке
            app_logger.error(f"Failed to add schedule to DB: {e}")
            return None

        finally:
            session.close()  # Закрываем сессию после всех операций

    def deactivate_schedule(self, schedule_id):
        """Деактивация записи из таблицы Schedule по id"""
        app_logger.debug("deactivate_schedule вызывается.")
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

    def activate_schedule(self, schedule_id):
        """Активация записи из таблицы Schedule по id"""
        app_logger.debug("activate_schedule вызывается.")
        session = self.Session()
        try:
            schedule = session.query(Schedule).filter_by(id=schedule_id).first()

            if schedule:
                # Активация расписания
                schedule.is_active = True
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
        #app_logger.debug("get_active_schedules вызывается.")
        session = self.Session()
        try:
            schedules = session.query(Schedule).filter_by(is_active=True).all()
            return [schedule.to_dict() for schedule in schedules]
        except Exception as e:
                session.rollback()
                raise
        finally:
            session.close()
            
    def schedule_exists(self, schedule_id):
        """Проверка существования расписания по id"""
        app_logger.debug("schedule_exists вызывается.")
        session = self.Session()
        try:
            exists_query = session.query(Schedule).filter_by(id=schedule_id).first() is not None
            return exists_query
        finally:
             session.close()

    def get_all_schedules(self):
        """Получить все расписания (активные и неактивные)"""
        app_logger.debug("get_all_schedules вызывается.")
        session = self.Session()
        try:
            schedules = session.query(Schedule).all()
            return [s.to_dict() for s in schedules]
        finally:
             session.close()
        
    def get_schedule_by_id(self, schedule_id):
        """Получить конкретное расписание по id"""
        app_logger.debug("get_schedule_by_id вызывается.")
        session = self.Session()
        try:
            # Получаем расписание по id
            schedule = session.query(Schedule).filter_by(id=schedule_id).first()
            # Возвращаем найденное расписание или None, если не найдено
            return schedule.to_dict()
        except Exception as e:
                session.rollback()
                raise
        finally:
            session.close()
        
    def delete_schedule(self, schedule_id):
        """Удаляет расписание и связанные с ним логи запросов по id"""
        app_logger.debug("delete_schedule вызывается.")
        session = self.Session()
        try:
            # Ищем расписание по ID
            schedule = session.query(Schedule).filter_by(id=schedule_id).first()

            if schedule:
                # Удаляем расписание (это также удалит связанные логи из-за ondelete='CASCADE')
                session.delete(schedule)
                session.commit()
                
                app_logger.info(f"Schedule with ID: {schedule_id} deleted successfully.")
                return True
            else:
                app_logger.warning(f"Schedule with ID: {schedule_id} not found.")
                return False
        except Exception as e:
            session.rollback()  # Откат транзакции при ошибке
            app_logger.error(f"Failed to delete schedule with ID {schedule_id}: {e}")
            return False
        finally:
            session.close()
 
    def get_all_schedules_filtered(self, offset, limit, sort_by, sort_order, **filters):
        """Получить все расписания (активные и неактивные) с поддержкой пагинации, фильтрации и сортировки."""
        if filters is None:
            filters = {}
        
        app_logger.debug("get_all_schedules вызывается с фильтрацией и сортировкой.")
        session = self.Session()
        try:
            query = session.query(Schedule)

            # Применяем фильтры
            for key, value in filters.items():
                if value is not None and hasattr(Schedule, key):
                    query = query.filter(getattr(Schedule, key) == value)
                    app_logger.debug(f"Применяем фильтр: {key} = {value}")

            # Применяем сортировку
            if sort_by and hasattr(Schedule, sort_by):
                if sort_order == 'desc':
                    query = query.order_by(desc(getattr(Schedule, sort_by)))
                else:
                    query = query.order_by(asc(getattr(Schedule, sort_by)))

            # Применяем пагинацию
            schedules = query.offset(offset).limit(limit).all()
            return [s.to_dict() for s in schedules]  # Преобразуем записи в словари
        finally:
            session.close()


    def update_last_run(self, schedule_id, last_run):
        session = Session()
        try:
            schedule = session.query(Schedule).filter_by(id=schedule_id).first()
            if schedule:
                schedule.last_run = last_run
                session.commit()
        except Exception as e:
                session.rollback()
                raise
        finally:
            session.close()

    def update_schedule_request(self, id, url=None, method=None, post_data=None):
        session = Session()
        try:
            schedule = session.query(Schedule).filter_by(id=id).first()
            if schedule:
                if url:
                    schedule.url = url
                if method:
                    schedule.method = method
                if post_data:
                    schedule.data = json.dumps(post_data)
                session.commit()
                return True
            else: 
                return False
        except Exception as e:
                session.rollback()
                return False
        finally:
            session.close()

    
    def update_schedule_time(self, id, schedule_type=None, interval=None, time_of_day=None):
        session = Session()
        try:
            schedule = session.query(Schedule).filter_by(id=id).first()
            if schedule:
                if schedule_type:
                    schedule.schedule_type = schedule_type
                if interval:
                    schedule.interval = interval
                if time_of_day:
                    schedule.time_of_day = json.dumps(time_of_day)
                session.commit()
                return True
            else: 
                return False
        except Exception as e:
                session.rollback()
                return False
        finally:
            session.close()