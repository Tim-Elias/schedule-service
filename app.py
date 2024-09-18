from flask import Flask, render_template, jsonify, request, redirect, url_for
from functools import wraps
from flask import request, redirect, url_for, session, flash
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, JWTManager
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
#app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY')  # Замените на более безопасный ключ в продакшене

app.secret_key=os.getenv('SECRET_KEY')

jwt = JWTManager(app)

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def jwt_optional(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = session.get('access_token')
        if token:
            try:
                # Устанавливаем токен в заголовок авторизации для проверки
                request.headers.environ['HTTP_AUTHORIZATION'] = f'Bearer {token}'
                verify_jwt_in_request()
            except:
                # Если токен недействителен или другая ошибка, удаляем его из сессии и перенаправляем на логин
                session.pop('access_token', None)
                flash('Invalid session, please log in again.', 'danger')
                return redirect(url_for('login'))
        else:
            return redirect(url_for('login'))
        return fn(*args, **kwargs)
    return wrapper



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


# Инициализация планировщика
def initialize_scheduler():
    with app.app_context():
        schedules = db.get_active_schedules()
        for schedule in schedules:
            if schedule.schedule_type == 'interval':
                interval_in_seconds = schedule.interval * 60
                scheduler.add_job(execute_schedule, 'interval', seconds=interval_in_seconds, args=[schedule.id])
            elif schedule.schedule_type == 'daily':
                # Время выполнения
                run_time = schedule.time_of_day
                scheduler.add_job(
                    execute_schedule,
                    'cron',
                    hour=run_time.hour, 
                    minute=run_time.minute, 
                    second=0,
                    args=[schedule.id]
                )




# Маршрут для главной страницы
@app.route('/')
def index():
    if 'jwt_token' in request.cookies:
        return redirect('/active_schedules')  # Перенаправляем авторизованных пользователей на активные расписания
    return render_template('login.html')



# Маршрут для входа (авторизации)
@app.route('/auth', methods=['POST'])
def auth():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    # Проверяем пользователя в базе данных
    if not db.user_exists(username) or not db.check_password( username, password):
        return jsonify({"msg": "Bad username or password"}), 401

    # Генерируем JWT токен
    
    access_token = create_access_token(identity=username)
    session['access_token'] = access_token
    return jsonify(access_token=access_token)

@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

"""@app.route('/validate_token', methods=['GET'])
@jwt_optional()
def validate_token():
    # Если токен действителен, возвращаем успешный ответ
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200
"""
# Защищённый маршрут
@app.route('/active_schedules')
@jwt_optional
def protected():
    return render_template('active_schedules.html')
    



# Маршрут деталей о расписании
@app.route('/schedule_details', methods=['GET'])
@jwt_optional
def schedule_details():
    schedule_id = request.args.get('id', type=int)
    if not schedule_id:
        return redirect(url_for('get_all_schedules'))
    
    schedule = db.get_schedule_by_id(schedule_id)
    logs = db.get_logs_by_schedule(schedule_id)
    return render_template('schedule_details.html', schedule=schedule, logs=logs)

# Страница всех расписаний
@app.route('/all_schedules', methods=['GET'])
@jwt_optional
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
        schedule_type = data.get('schedule_type')  # Новый параметр типа расписания
        post_data = data.get('data', None)  # Данные для POST-запроса (если это POST)

        logging.info(f"Received schedule data: method={method}, url={url}, schedule_type={schedule_type}, post_data={post_data}")

        # Проверяем наличие обязательных полей
        if not method or not url or not schedule_type:
            logging.error("Missing required fields: Method, URL, and Schedule Type are required")
            return jsonify({"msg": "Method, URL, and schedule_type are required"}), 400

        # Разные обработки в зависимости от типа расписания
        if schedule_type == 'interval':
            interval = data.get('interval')  # Интервал в минутах
            if not interval:
                logging.error("Missing interval for interval schedule")
                return jsonify({"msg": "Interval is required for interval schedule"}), 400

            interval_in_seconds = int(interval) * 60
            logging.debug(f"Converted interval to seconds: {interval_in_seconds}")

            # Добавляем новое расписание в базу данных
            new_schedule = db.add_schedule(
                method=method,
                url=url,
                data=post_data,
                interval=interval,  # Интервал сохраняем
                schedule_type='interval',
                last_run=datetime.utcnow()
            )

            # Логируем успешное добавление в БД
            logging.info(f"New interval schedule added to database with ID: {new_schedule.id}")

            # Добавляем задачу в планировщик по интервалу
            scheduler.add_job(
                execute_schedule, 
                'interval', 
                seconds=interval_in_seconds, 
                args=[new_schedule.id], 
                id=f"schedule_{new_schedule.id}"
            )
            # Запускаем задачу немедленно после создания
            execute_schedule(new_schedule.id)
            logging.info(f"Scheduled interval job created and executed for schedule ID: {new_schedule.id}")

        elif schedule_type == 'daily':
            time_of_day = data.get('time_of_day')  # Время выполнения задачи
            if not time_of_day:
                logging.error("Missing time_of_day for daily schedule")
                return jsonify({"msg": "Time of day is required for daily schedule"}), 400

            # Преобразуем строку времени в объект времени
            time_of_day_obj = datetime.strptime(time_of_day, '%H:%M').time()

            # Добавляем новое ежедневное расписание в базу данных
            new_schedule = db.add_schedule(
                method=method,
                url=url,
                data=post_data,
                schedule_type='daily',
                time_of_day=time_of_day_obj,  # Время выполнения
                last_run=None
            )

            # Логируем успешное добавление в БД
            logging.info(f"New daily schedule added to database with ID: {new_schedule.id}")

            # Добавляем задачу в планировщик для ежедневного выполнения
            scheduler.add_job(
                execute_schedule, 
                'cron', 
                hour=time_of_day_obj.hour, 
                minute=time_of_day_obj.minute, 
                second=0,
                args=[new_schedule.id],
                id=f"schedule_{new_schedule.id}"
            )

            logging.info(f"Scheduled daily job created for schedule ID: {new_schedule.id}")

        else:
            logging.error("Invalid schedule type provided")
            return jsonify({"msg": "Invalid schedule type"}), 400

        

        # Логируем успешное выполнение задачи
        logging.info(f"Scheduled job executed for schedule ID: {new_schedule.id}")

        return jsonify({"msg": "Schedule created and task added successfully"}), 201

    except Exception as e:
        # Логируем ошибку и возвращаем информацию для отладки
        logging.error(f"Error adding schedule: {e}")
        return jsonify({"msg": "Failed to create schedule", "error": str(e)}), 500


# Получение списка активных расписаний
@app.route('/schedules', methods=['GET'])
@jwt_required()
def get_schedules():
    schedules = db.get_active_schedules()
    schedules_data = []

    for s in schedules:
        schedule_info = {
            "id": s.id,
            "method": s.method,
            "url": s.url,
            "last_run": s.last_run,
            "is_active": s.is_active
        }

        if s.schedule_type == 'interval':
            schedule_info['schedule_type'] = 'interval'
            schedule_info['interval'] = s.interval
        elif s.schedule_type == 'daily':
            schedule_info['schedule_type'] = 'daily'
            schedule_info['time_of_day'] = s.time_of_day.strftime('%H:%M') if s.time_of_day else None
        
        schedules_data.append(schedule_info)
    
    return jsonify(schedules=schedules_data), 200



# Получение всех расписаний
@app.route('/all_schedules_get', methods=['GET'])
@jwt_required()
def get_all_schedules():
    logging.debug('Request to /all_schedules_get received')
    schedules = db.get_all_schedules()
    schedules_data = []

    for s in schedules:
        schedule_info = {
            "id": s.id,
            "method": s.method,
            "url": s.url,
            "last_run": s.last_run,
            "is_active": s.is_active
        }

        if s.schedule_type == 'interval':
            schedule_info['schedule_type'] = 'interval'
            schedule_info['interval'] = s.interval
        elif s.schedule_type == 'daily':
            schedule_info['schedule_type'] = 'daily'
            schedule_info['time_of_day'] = s.time_of_day.strftime('%H:%M') if s.time_of_day else None
        
        schedules_data.append(schedule_info)

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

    if schedule.schedule_type == 'interval':
        # Преобразуем интервал в секунды для интервала
        interval_in_seconds = int(schedule.interval) * 60
        # Добавляем задачу в планировщик
        scheduler.add_job(
            execute_schedule, 
            'interval', 
            seconds=interval_in_seconds, 
            args=[schedule.id], 
            id=f"schedule_{schedule.id}"
        )
        # Немедленный запуск задачи
        execute_schedule(schedule.id)
        logging.info(f"Scheduled job created and executed for schedule ID: {schedule.id} (interval)")
    
    elif schedule.schedule_type == 'daily':
        # Преобразуем время в строковый формат для планировщика
        schedule_time = schedule.time_of_day.strftime('%H:%M:%S')
        # Добавляем задачу в планировщик
        scheduler.add_job(
            execute_schedule, 
            'cron', 
            hour=schedule.time_of_day.hour, 
            minute=schedule.time_of_day.minute, 
            second=schedule.time_of_day.second, 
            args=[schedule.id], 
            id=f"schedule_{schedule.id}"
        )
        logging.info(f"Scheduled job created for schedule ID: {schedule.id} (daily at {schedule.time_of_day})")

    
    
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
    job_id = f"schedule_{id}"
    scheduler.remove_job(job_id)
    return jsonify({"message": "Schedule deactivated"}), 200


# Пример функции обновления расписания
@app.route('/schedule/<int:schedule_id>', methods=['PUT'])
def update_schedule(schedule_id):
    data = request.json
    
    # Логика поиска расписания в базе данных
    schedule = db.get_schedule_by_id(schedule_id)
    
    if schedule is None:
        return jsonify({'error': 'Schedule not found'}), 404
    
    # Обновляем поля расписания
    schedule.method = data['method']
    schedule.url = data['url']
    
    if data.get('schedule_type') == 'interval':
        schedule.schedule_type = 'interval'
        schedule.interval = data['interval']
        schedule.time_of_day = None  # Убираем время, если было
    
    elif data.get('schedule_type') == 'daily':
        schedule.schedule_type = 'daily'
        schedule.time_of_day = data['time_of_day']
        schedule.interval = None  # Убираем интервал, если был

    schedule.data = data.get('data')
    
    # Сохраняем обновленное расписание
    db.update_schedule(schedule)
    
    return jsonify({'message': 'Schedule updated successfully'}), 200



if __name__ == '__main__':
    with app.app_context():
        initialize_scheduler()
    app.run(debug=True)

