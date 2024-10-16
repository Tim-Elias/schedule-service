from sqlalchemy import Column, Integer, Text,  DateTime, ForeignKey, String
from datetime import datetime
import json
import codecs
from app.database.db_setup import Base 

# Модель RequestLog
class RequestLog(Base):
    __tablename__ = 'request_log'
    
    id = Column(String(36), primary_key=True, autoincrement=False)
    schedule_id = Column(String(36), ForeignKey('schedule.id', ondelete='CASCADE'), nullable=True)
    response = Column(Text, nullable=False)  # Ответ от сервера
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)  # Время выполнения запроса
    status_code = Column(Integer, nullable=True)  # Новый столбец для кода статуса

    def __repr__(self):
        return f'<RequestLog {self.id} {self.timestamp} {self.status_code}>'
    
    

    def to_dict(self):
        # Используем codecs для декодирования с удалением BOM
        response_str = codecs.decode(self.response.encode('utf-8'), 'utf-8-sig')
        return {
            "id": self.id,
            "schedule_id": self.schedule_id,
            "response": json.loads(response_str),
            "timestamp": self.timestamp,
            "status_code": self.status_code
        }

