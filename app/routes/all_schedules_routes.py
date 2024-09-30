from flask import Blueprint
from flask_jwt_extended import  jwt_required, get_jwt_identity
from flask import  render_template, jsonify
import logging


all_schedules_bp = Blueprint('all_schedules', __name__)


# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Страница всех расписаний
@all_schedules_bp.route('/all_schedules', methods=['GET'])
def all_schedules():
    return render_template('all_schedules.html')

# Получение всех расписаний
@all_schedules_bp.route('/all_schedules_get', methods=['GET'])
@jwt_required()
def get_all_schedules():
    current_user = get_jwt_identity()  # Получение информации о текущем пользователе
    logging.debug("Current user: %s", current_user)
    logging.debug("JWT token is valid")
    from app.database.schedule_manager import ScheduleManager
    db = ScheduleManager()
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