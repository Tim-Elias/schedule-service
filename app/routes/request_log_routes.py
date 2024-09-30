from flask import Blueprint
from flask_jwt_extended import jwt_required
from flask import jsonify

request_log_bp = Blueprint('request_log', __name__)


# Получение активных логов
@request_log_bp.route('/logs/active', methods=['GET'])
@jwt_required()
def get_active_logs():
    from app.database.request_log_manager import RequestLogManager
    db_l = RequestLogManager()
    from app.database.schedule_manager import ScheduleManager
    db_s = ScheduleManager()
    # Получаем все активные расписания
    active_schedules = db_s.get_active_schedules()
    logs = []
    for schedule in active_schedules:
        schedule_logs = db_l.get_logs_by_schedule(schedule.id)
        logs.extend(schedule_logs)
    
    logs_data = [{
        "schedule_id": log.schedule_id,
        "response": log.response,
        "timestamp": log.timestamp
    } for log in logs]

    return jsonify(logs=logs_data), 200

# Получение логов по id
@request_log_bp.route('/logs/<int:schedule_id>', methods=['GET'])
@jwt_required()
def get_logs_by_schedule_id(schedule_id):
    from app.database.request_log_manager import RequestLogManager
    db = RequestLogManager()
    logs=db.get_logs_by_schedule(schedule_id)
    logs_data = [{
        "schedule_id": log.schedule_id,
        "response": log.response,
        "timestamp": log.timestamp
    } for log in logs]
    return jsonify(logs=logs_data), 200