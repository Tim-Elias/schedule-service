from app.models import RequestLog  
from app.database.db_globals import Session
from sqlalchemy import asc, desc
from math import ceil
import uuid
import logging

# Настройка логирования
app_logger = logging.getLogger('app_logger')

class RequestLogManager:
    def __init__(self):
        self.Session = Session

    def get_logs_by_schedule(self, schedule_id, offset, limit):
        """Получить все логи для заданного расписания"""
        from app.models import Schedule
        session = self.Session()
        try:
            query = session.query(RequestLog)
            query = query.filter_by(schedule_id = schedule_id)
            # Применяем пагинацию
            logs = query.offset(offset).limit(limit).all()
            #logs = session.query(RequestLog).offset(offset).limit(limit).filter_by(schedule_id=schedule_id).all()
            return [log.to_dict() for log in logs]
        except Exception as e:
                session.rollback()
                raise
        finally:
             session.close()
    

    def add_request_log(self, schedule_id, response, status_code):
        """
        Добавляем новую запись в таблицу RequestLog.
        Теперь сохраняем также метод, URL и данные запроса.
        """
        session = self.Session()
        try:
            id = str(uuid.uuid4())
            new_log = RequestLog(
                id = id,
                schedule_id=schedule_id,
                response=response,
                status_code=status_code
            )
            session.add(new_log)
            session.commit()
        except Exception as e:
                session.rollback()
                raise
        finally:
             session.close()
        

    def get_request_logs(self):
        """
        Получить все записи из таблицы RequestLog.
        Логи теперь содержат метод, URL и данные запроса.
        """
        session = self.Session()
        try:
            logs = session.query(RequestLog).all()
            return [log.to_dict() for log in logs]
        except Exception as e:
                session.rollback()
                raise
        finally:
             session.close()
        

    def get_request_logs_filtered(self, offset, limit, sort_by, sort_order, **filters):
        """
        Получить все записи из таблицы RequestLog с поддержкой пагинации, фильтрации и сортировки.
        Логи теперь содержат метод, URL и данные запроса.
        """
        app_logger.debug("get_request_logs вызывается с фильтрацией, сортировкой и пагинацией.")
        session = self.Session()
        try:
            query = session.query(RequestLog)

            # Применяем фильтры
            for key, value in filters.items():
                if value is not None and hasattr(RequestLog, key):
                    query = query.filter(getattr(RequestLog, key) == value)
                    app_logger.debug(f"Применяем фильтр: {key} = {value}")

            # Применяем сортировку
            if sort_by and hasattr(RequestLog, sort_by):
                if sort_order == 'desc':
                    query = query.order_by(desc(getattr(RequestLog, sort_by)))
                    app_logger.debug(f"Сортируем по {sort_by} в порядке убывания.")
                else:
                    query = query.order_by(asc(getattr(RequestLog, sort_by)))
                    app_logger.debug(f"Сортируем по {sort_by} в порядке возрастания.")

            # Применяем пагинацию
            logs = query.offset(offset).limit(limit).all()
            app_logger.debug(f"Получено {len(logs)} записей из RequestLog.")
            app_logger.debug(f"Получены логи {logs}.")
            return [log.to_dict() for log in logs]  # Преобразуем записи в словари

        except Exception as e:
            app_logger.error(f"Ошибка при получении логов: {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()

        
    
