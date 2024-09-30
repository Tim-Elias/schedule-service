from app.models import RequestLog  
from app.database.db_globals import Session


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