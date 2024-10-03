from app.models import RequestLog  
from app.database.db_globals import Session
from math import ceil


class RequestLogManager:
    def __init__(self):
        self.Session = Session

    def get_logs_by_schedule(self, schedule_id):
        """Получить все логи для заданного расписания"""
        session = self.Session()
        try:
            logs = session.query(RequestLog).filter_by(schedule_id=schedule_id).all()
            return logs
        finally:
            session.close()

    def add_request_log(self, schedule_id, response):
        """
        Добавляем новую запись в таблицу RequestLog.
        Теперь сохраняем также метод, URL и данные запроса.
        """
        session = self.Session()
        new_log = RequestLog(
            schedule_id=schedule_id,
            response=response
        )
        session.add(new_log)
        session.commit()
        session.close()

    def get_request_logs(self):
        """
        Получить все записи из таблицы RequestLog.
        Логи теперь содержат метод, URL и данные запроса.
        """
        session = self.Session()
        logs = session.query(RequestLog).all()
        session.close()
        return logs
    
    def get_logs_by_schedule_paginated(self, schedule_id, page=1, per_page=10):
        """Получить логи по schedule_id с поддержкой пагинации"""
        session = self.Session()
        try:
            query = session.query(RequestLog).filter_by(schedule_id=schedule_id)
            total_logs = query.count()  # Общее количество логов для данного расписания
            logs = query.order_by(RequestLog.timestamp.desc()) \
                         .limit(per_page) \
                         .offset((page - 1) * per_page) \
                         .all()
            return logs, total_logs
        finally:
            session.close()

    def get_active_logs_paginated(self, active_schedule_ids, page=1, per_page=10):
        """
        Получить логи для активных расписаний с пагинацией
        :param active_schedule_ids: список ID активных расписаний
        :param page: номер страницы
        :param per_page: количество элементов на странице
        """
        session = self.Session()
        try:
            query = session.query(RequestLog).filter(RequestLog.schedule_id.in_(active_schedule_ids))
            total_logs = query.count()  # Подсчитываем общее количество логов
            logs = query.order_by(RequestLog.timestamp.desc()) \
                         .limit(per_page) \
                         .offset((page - 1) * per_page) \
                         .all()
            return logs, total_logs
        finally:
            session.close()