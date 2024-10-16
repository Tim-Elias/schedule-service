from sqlalchemy import Column, Integer, String, Text, Time, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.database.db_setup import Base 
import json


class Schedule(Base):
    __tablename__ = 'schedule'
    
    id = Column(String(36), primary_key=True, autoincrement=False)
    method = Column(String(10), nullable=False)
    url = Column(String(255), nullable=False)
    data = Column(Text, nullable=True)
    interval = Column(Integer, nullable=True)  # Оставим nullable для случаев с типом "daily"
    time_of_day = Column(Time, nullable=True)  # Время выполнения для типа "daily"
    schedule_type = Column(String(50), nullable=False, default='interval')  # Тип расписания
    last_run = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

    request_logs = relationship("RequestLog", backref="schedule")

    def __repr__(self):
        return f'<Schedule {self.id} {self.method} {self.url} {self.schedule_type}>'
    
    def to_dict(self):
        schedule_dict = {
            "id": self.id,
            "method": self.method,
            "url": self.url,
            "data": json.loads(self.data) if self.data else {},  # Защита от ошибок при отсутствии данных
            "schedule_type": self.schedule_type,
            "last_run": self.last_run,
            "is_active": self.is_active
        }

        if self.schedule_type == 'interval':
            schedule_dict['interval'] = self.interval
        elif self.schedule_type == 'daily':
            if self.time_of_day:
                schedule_dict['time_of_day'] = self.time_of_day.strftime('%H:%M:%S')  # Преобразуем объект Time в строку
            else:
                schedule_dict['time_of_day'] = None  # Убедитесь, что None обработан правильно

        return schedule_dict
