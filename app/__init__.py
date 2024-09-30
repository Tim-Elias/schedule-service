from flask import Flask
from flask_jwt_extended import JWTManager
import os
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from app.database import init_db, set_db_globals
from app.routes import register_routes
from app.scheduler import initialize_scheduler, start_scheduler
from app.database.user_manager import UserManager

load_dotenv()

oauth = OAuth()

def create_app():
    app = Flask(__name__)
    
    # Настройки приложения
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    
    # Настройка JWT
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')  # Секретный ключ для JWT
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  # Время истечения токена доступа, пример
    
    # Инициализация JWTManager
    jwt = JWTManager(app)
    oauth.init_app(app)

    google = oauth.register(
        name='google',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        access_token_url='https://accounts.google.com/o/oauth2/token',
        access_token_params=None,
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        authorize_params=None,
        userinfo_endpoint='https://www.googleapis.com/oauth2/v1/userinfo',
        client_kwargs={'scope': 'openid email profile'},  # Update the scopes here
    )

    
    
    # Инициализация базы данных
    engine, Session, Base = init_db(app)

    db = UserManager()
    password=os.getenv('PASSWORD')
    username=os.getenv('LOGIN')
    db.add_user_password(username, password)

    # Установка глобальных переменных для работы с базой данных
    set_db_globals(engine, Session, Base)
    
    # Регистрация маршрутов
    register_routes(app)
    # Регистрация маршрутов
    from app.routes import google_auth_bp
    app.register_blueprint(google_auth_bp)
    # Передаем объект google в новый файл аутентификации
    google_auth_bp.oauth = google
    
    # Инициализация планировщика после инициализации приложения и базы данных
    with app.app_context():
        initialize_scheduler()  # Инициализируем расписания в планировщике
        start_scheduler()  # Запускаем планировщик
    
    return app
