from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import logging
from db_manager import DatabaseManager
import os
from dotenv import load_dotenv

db = DatabaseManager()

# Создаем таблицы
db.create_tables()

load_dotenv()

app = Flask(__name__)

# Секретный ключ для подписи JWT
app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY')  # Замените на более безопасный ключ в продакшене


jwt = JWTManager(app)

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')





# Запуск планировщика
# Создание планировщика
scheduler = BackgroundScheduler()
scheduler.start()

def execute_schedule(schedule_id):
    logging.debug(f"Executing schedule with ID: {schedule_id}")
    schedule = db.get_schedule_by_id(schedule_id)
    if not schedule:
        logging.error('No schedule found with the given ID')
        return

    logging.debug(f"Schedule details: {schedule}")

    try:
        # Инициализируем переменные для метода, URL и данных запроса
        method = schedule.method
        url = schedule.url
        data = schedule.data if schedule.method == 'POST' else None
        
        # Выполняем запрос в зависимости от метода
        if method == 'GET':
            response = requests.get(url)
        elif method == 'POST':
            response = requests.post(url, data=data)
        
        logging.debug(f"Response: {response.text}")
        
        # Логируем результат запроса
        db.add_request_log(
            schedule_id=schedule.id,
            response=response.text
        )
        
        # Обновляем время последнего выполнения
        schedule.last_run = datetime.utcnow()
        db.update_schedule(schedule)
        logging.info(f"Schedule {schedule.id} successfully executed at {schedule.last_run}")

    except Exception as e:
        logging.error(f"Error during request: {e}")



def initialize_scheduler():
    with app.app_context():
        schedules = db.get_active_schedules()
        print(schedules)
        for schedule in schedules:
            interval_in_seconds = schedule.interval * 60
            scheduler.add_job(execute_schedule, 'interval', seconds=interval_in_seconds, args=[schedule.id])




# Маршрут для главной страницы
@app.route('/')
def index():
    return render_template('login.html')

"""# Маршрут для регистрации
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.json.get('username', None)
        password = request.json.get('password', None)

        if not username or not password:
            return jsonify({"msg": "Username and password are required"}), 400

        if db.user_exists(username):
            return jsonify({"msg": "Username already taken"}), 400

        new_user = db.add_user(username, password)
        db.session.add(new_user)
        db.session.commit()"""

# Маршрут для входа (авторизации)
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    # Проверяем пользователя в базе данных
    if not db.user_exists(username) or not db.check_password( username, password):
        return jsonify({"msg": "Bad username or password"}), 401

    # Генерируем JWT токен
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)


@app.errorhandler(401)
def unauthorized_error(error):
    return jsonify({"msg": "Unauthorized access"}), 401

# Защищённый маршрут
@app.route('/active_schedules')
def protected():
    return render_template('active_schedules.html')
    



# Маршрут деталей о расписании
@app.route('/schedule_details', methods=['GET'])
def schedule_details():
    schedule_id = request.args.get('id', type=int)
    if not schedule_id:
        return redirect(url_for('get_all_schedules'))
    
    schedule = db.get_schedule_by_id(schedule_id)
    logs = db.get_logs_by_schedule(schedule_id)
    return render_template('schedule_details.html', schedule=schedule, logs=logs)

# Страница всех расписаний
@app.route('/all_schedules', methods=['GET'])
def all_schedules():
    return render_template('all_schedules.html')

# Добавить расписание
@app.route('/schedule', methods=['POST'])
@jwt_required()
def add_schedule():
    try:
        data = request.json
        method = data.get('method')
        url = data.get('url')
        interval = data.get('interval')  # Интервал в минутах
        post_data = data.get('data', None)  # Данные для POST-запроса (если это POST)
        
        # Логируем полученные данные для диагностики
        logging.info(f"Received schedule data: method={method}, url={url}, interval={interval}, post_data={post_data}")
        
        if not method or not url or not interval:
            logging.error("Missing required fields: Method, URL, and Interval are required")
            return jsonify({"msg": "Method, URL, and interval are required"}), 400

        # Преобразуем интервал в секунды
        interval_in_seconds = int(interval) * 60
        
        # Логируем преобразованный интервал
        logging.debug(f"Converted interval to seconds: {interval_in_seconds}")

        # Добавляем новое расписание в базу данных
        new_schedule = db.add_schedule(
            method=method,
            url=url,
            data=post_data,
            interval=interval,
            last_run=datetime.utcnow()
        )
        
        if not new_schedule:
            raise Exception("Failed to add schedule to database")

        # Логируем успешное добавление расписания в БД
        logging.info(f"New schedule added to database with ID: {new_schedule.id}")
        
        # Добавляем задачу в планировщик
        scheduler.add_job(
            execute_schedule, 
            'interval', 
            seconds=interval_in_seconds, 
            args=[new_schedule.id], 
            id=f"schedule_{new_schedule.id}"
        )

        # Логируем успешное добавление задачи в планировщик
        logging.info(f"Scheduled job created for schedule ID: {new_schedule.id}")

        return jsonify({"msg": "Schedule created and task added successfully"}), 201

    except Exception as e:
        # Логируем ошибку и возвращаем информацию для отладки
        logging.error(f"Error adding schedule: {e}")
        return jsonify({"msg": "Failed to create schedule", "error": str(e)}), 500


# Получение списка расписаний
@app.route('/schedules', methods=['GET'])
@jwt_required()
def get_schedules():
    schedules = db.get_active_schedules()
    schedules_data = [{
        "id": s.id,
        "method": s.method,
        "url": s.url,
        "interval": s.interval,
        "last_run": s.last_run
    } for s in schedules]

    return jsonify(schedules=schedules_data), 200


# Получение всех расписаний
@app.route('/all_schedules_get', methods=['GET'])
@jwt_required()
def get_all_schedules():
    logging.debug('Request to /all_schedules_get received')
    schedules = db.get_all_schedules()
    schedules_data = [{
        "id": s.id,
        "method": s.method,
        "url": s.url,
        "interval": s.interval,
        "last_run": s.last_run,
        "is_active": s.is_active
    } for s in schedules]

    logging.debug('Schedules data prepared')
    return jsonify(schedules=schedules_data), 200


# Получение активных логов
@app.route('/logs/active', methods=['GET'])
@jwt_required()
def get_active_logs():
    # Получаем все активные расписания
    active_schedules = db.get_active_schedules()
    logs = []
    for schedule in active_schedules:
        schedule_logs = db.get_logs_by_schedule(schedule.id)
        logs.extend(schedule_logs)
    
    logs_data = [{
        "schedule_id": log.schedule_id,
        "response": log.response,
        "timestamp": log.timestamp
    } for log in logs]

    return jsonify(logs=logs_data), 200

# Получение логов по id
@app.route('/logs/<int:schedule_id>', methods=['GET'])
@jwt_required()
def get_logs_by_schedule_id(schedule_id):
    logs=db.get_logs_by_schedule( schedule_id)
    logs_data = [{
        "schedule_id": log.schedule_id,
        "response": log.response,
        "timestamp": log.timestamp
    } for log in logs]
    return jsonify(logs=logs_data), 200


# Активация расписания
@app.route('/schedule/<int:id>/activate', methods=['PATCH'])
@jwt_required()
def activate_schedule(id):
    schedule = db.get_schedule_by_id(id)
    if not schedule:
        return jsonify({"message": "Schedule not found"}), 404
    
    schedule.is_active = True
    db.update_schedule(schedule)
    return jsonify({"message": "Schedule activated"}), 200


# Деактивация расписания
@app.route('/schedule/<int:id>/deactivate', methods=['PATCH'])
@jwt_required()
def deactivate_schedule(id):
    schedule = db.get_schedule_by_id(id)
    if not schedule:
        return jsonify({"message": "Schedule not found"}), 404
    
    schedule.is_active = False
    db.update_schedule(schedule)
    return jsonify({"message": "Schedule deactivated"}), 200

if __name__ == '__main__':
    with app.app_context():
        initialize_scheduler()
    app.run(debug=True)

