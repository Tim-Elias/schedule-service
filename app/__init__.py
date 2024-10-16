from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from flask_restx import Api
import os
from flask import jsonify, request, g
from request_logger import RequestLogHandler
from dotenv import load_dotenv
from app.database import init_db, set_db_globals
from app.routes import register_routes
from app.scheduler.scheduler import initialize_scheduler, start_scheduler



load_dotenv()



def create_app():
    import request_logger, app_logger
    app = Flask(__name__)
    CORS(app, resources={r"/*": {
        "origins": "*",
        "allow_headers": ["Content-Type", "Authorization"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "supports_credentials": True
    }})
    # Настройки приложения
    database_url = os.getenv('DATABASE_URL')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    
    # Настройка JWT
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')  # Секретный ключ для JWT
    from datetime import timedelta

    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)  # срок действия access токена
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)    # срок действия refresh токена

    app.config['PASSWORD']=os.getenv('PASSWORD')
    app.config['LOGIN']=os.getenv('LOGIN')
    
    # Инициализация JWTManager
    jwt = JWTManager(app)

    # Инициализация базы данных
    engine, Session, Base = init_db(database_url)

    # Установка глобальных переменных для работы с базой данных
    set_db_globals(engine, Session, Base)
    

    # Инициализация API
    api = Api(app, doc='/swagger')  # Создаем экземпляр Api

    # Регистрация маршрутов
    register_routes(api)  # Передаем экземпляр Api в функцию регистрации маршрутов
    
    # Инициализация планировщика после инициализации приложения и базы данных
    with app.app_context():
        initialize_scheduler()  # Инициализируем расписания в планировщике
        start_scheduler()  # Запускаем планировщик

    
    @app.before_request
    def before_request():
        # List of routes that do not require authentication
        open_routes = ['/auth', '/swagger.json', '/swaggerui/', '/swagger']

        # Skip authentication check for specific open routes
        if any(request.path.startswith(route) for route in open_routes):
            return  # No need to verify JWT

        # Skip authentication for OPTIONS requests (CORS preflight requests)
        if request.method == 'OPTIONS':
            return  # No need to verify JWT for preflight requests

        try:
            # Verify JWT token in the request
            verify_jwt_in_request()

            # Get user identity from the JWT token
            g.user = get_jwt_identity()
            print(f"Authenticated user: {g.user}")

        except Exception as e:
            # If there's an issue with the JWT (invalid, missing, etc.)
            return jsonify({"msg": "Missing or invalid token"}), 401


    @app.after_request
    def after_request(response):
        # Инициализация переменных для entity_name и entity_id
        entity_name = 'unknown'
        entity_id = 'N/A'

        # Определение сущности на основе пути
        if request.path.startswith('/schedule'):
            entity_name = 'schedule'
        elif request.path.startswith('/request_logs'):
            entity_name = 'request_log'

        # Поиск ID в аргументах запроса
        if request.view_args and 'id' in request.view_args:
            entity_id = request.view_args['id']

        # Determine action from HTTP method (GET, POST, etc.)
        action = request.method.lower()

        # Ensure that `g.user` is available and fallback to 'unknown' if not
        user_identity = g.get('user', 'unknown')

        # Log the request using the RequestLogHandler
        RequestLogHandler.log_request(
            entity_name=entity_name or 'unknown',
            entity_id=entity_id or 'N/A',
            url=request.url,
            user=user_identity,
            response_status=response.status_code,
            action=action,
            is_bulk=False  # Change this to True if the request is a bulk operation
        )

        return response
    
    return app