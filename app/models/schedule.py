from sqlalchemy import Column, Integer, String, Text, Time, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.database.db_setup import Base 


class Schedule(Base):
    __tablename__ = 'schedule'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
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