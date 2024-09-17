from sqlalchemy import create_engine, Column, String, Integer, Date, Time
from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import exists
import sqlalchemy
import logging
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv



load_dotenv()

#подгружаем базу данных
username = os.getenv('DB_USERNAME')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')
port = os.getenv('DB_PORT')
database = os.getenv('DB_DATABASE')

DATABASE_URL = f'postgresql://{username}:{password}@{host}:{port}/{database}'

# Создание базы данных и настройка SQLAlchemy
engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)
session = Session()
Base = sqlalchemy.orm.declarative_base()


# Модель Schedule
class Schedule(Base):
    __tablename__ = 'schedule'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    method = Column(String(10), nullable=False)
    url = Column(String(255), nullable=False)
    data = Column(Text, nullable=True)
    interval = Column(Integer, nullable=False)
    last_run = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)  # Новое поле для проверки активности

    request_logs = relationship("RequestLog", backref="schedule")

    def __repr__(self):
        return f'<Schedule {self.id} {self.method} {self.url}>'



# Модель RequestLog
class RequestLog(Base):
    __tablename__ = 'request_log'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    schedule_id = Column(Integer, ForeignKey('schedule.id', ondelete='SET NULL'), nullable=True)
    response = Column(Text, nullable=False)  # Ответ от сервера
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)  # Время выполнения запроса

    def __repr__(self):
        return f'<RequestLog {self.id} {self.timestamp}>'



# Определение модели для таблицы user_records
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    def set_password(self, password):
        """Создание хэша пароля"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Проверка пароля"""
        return check_password_hash(self.password_hash, password)



# Менеджер базы данных
class DatabaseManager:
    def __init__(self):
        self.engine = engine
        self.Session = Session

    def create_tables(self):
        """Создаем таблицы"""
        Base.metadata.create_all(self.engine)

    # Методы для работы с таблицей Schedule
    def add_schedule(self, method, url, data, interval, last_run):
        session = self.Session()  # Открываем сессию
        try:
            # Создаем объект Schedule
            new_schedule = Schedule(
                method=method,
                url=url,
                data=data,
                interval=interval,
                last_run=last_run
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
        session = self.Session()
        try:
            schedules = session.query(Schedule).filter_by(is_active=True).all()
            return schedules
        finally:
            session.close()


    def schedule_exists(self, schedule_id):
        """Проверка существования расписания по id"""
        session = self.Session()
        exists_query = session.query(Schedule).filter_by(id=schedule_id).first() is not None
        session.close()
        return exists_query

    def get_all_schedules(self):
        """Получить все расписания (активные и неактивные)"""
        session = self.Session()
        try:
            schedules = session.query(Schedule).all()
            return schedules
        finally:
            session.close()

    def get_logs_by_schedule(self, schedule_id):
        """Получить все логи для заданного расписания"""
        session = self.Session()
        try:
            logs = session.query(RequestLog).filter_by(schedule_id=schedule_id).all()
            return logs
        finally:
            session.close()

    
    def get_schedule_by_id(self, schedule_id):
        """Получить конкретное расписание по id"""
        session = self.Session()
        try:
            # Получаем расписание по id
            schedule = session.query(Schedule).filter_by(id=schedule_id).first()
        finally:
            # Закрываем сессию в блоке finally, чтобы гарантировать закрытие независимо от результата запроса
            session.close()

        # Возвращаем найденное расписание или None, если не найдено
        return schedule

    # Методы для работы с таблицей RequestLog
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

    def add_user(self, username, password):
        """Добавляем пользователя"""
        session = self.Session()
        new_user = User(user_id=username)
        new_user.set_password(password)  # Устанавливаем хэш пароля
        session.add(new_user)
        session.commit()
        session.close()

    def check_password(self, username, password):
        """Проверяем пароль пользователя"""
        session = self.Session()
        user = session.query(User).filter_by(user_id=username).first()
        session.close()
        if user and user.check_password(password):
            return True
        return False

    def update_user_password(self, username, new_password):
        """Обновляем пароль пользователя"""
        session = self.Session()
        user = session.query(User).filter_by(user_id=username).first()
        if user:
            user.set_password(new_password)  # Обновляем хэш пароля
            session.commit()
        session.close()

    def user_exists(self, username):
        """Проверка существования пользователя по имени"""
        session = self.Session()
        exists_query = session.query(exists().where(User.user_id == username)).scalar()
        session.close()
        return exists_query