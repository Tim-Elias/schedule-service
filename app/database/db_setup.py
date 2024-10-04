from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

def init_db(app):
    DATABASE_URL = app.config['SQLALCHEMY_DATABASE_URI']
    from app.models import RequestLog, User, Schedule
    engine = create_engine(DATABASE_URL, echo=False)
    Session = sessionmaker(bind=engine)
    # Создание всех таблиц
    Base.metadata.create_all(engine)

    return engine, Session, Base