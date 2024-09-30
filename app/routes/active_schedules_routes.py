from flask import Blueprint
from flask_jwt_extended import  jwt_required
from flask import render_template, jsonify, request
import logging
from datetime import datetime
from app.scheduler import execute_schedule, scheduler



active_schedules_bp = Blueprint('active_schedules', __name__)



# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Защищенная страница с активными расписаниями
@active_schedules_bp.route('/active_schedules')
def active_schedules():
    return render_template('active_schedules.html')

# Добавить расписание
@active_schedules_bp.route('/schedule', methods=['POST'])
@jwt_required()
def add_schedule():
    from app.database.schedule_manager import ScheduleManager
    db = ScheduleManager()
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
@active_schedules_bp.route('/schedules', methods=['GET'])
@jwt_required()
def get_schedules():
    from app.database.schedule_manager import ScheduleManager
    db = ScheduleManager()
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