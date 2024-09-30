from sqlalchemy import Column, Integer, Text,  DateTime, ForeignKey
from datetime import datetime
from app.database.db_setup import Base 

# Модель RequestLog
class RequestLog(Base):
    __tablename__ = 'request_log'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    schedule_id = Column(Integer, ForeignKey('schedule.id', ondelete='SET NULL'), nullable=True)
    response = Column(Text, nullable=False)  # Ответ от сервера
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)  # Время выполнения запроса

    def __repr__(self):
        return f'<RequestLog {self.id} {self.timestamp}>'