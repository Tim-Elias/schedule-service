from flask import Blueprint
from flask_jwt_extended import jwt_required
from flask import jsonify, request

request_log_bp = Blueprint('request_log', __name__)



# Получение активных логов с пагинацией
@request_log_bp.route('/logs/active', methods=['GET'])
@jwt_required()
def get_active_logs():
    from app.database.request_log_manager import RequestLogManager
    from app.database.schedule_manager import ScheduleManager

    db_l = RequestLogManager()
    db_s = ScheduleManager()

    # Параметры пагинации
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)

    # Получаем активные расписания
    active_schedules = db_s.get_active_schedules()
    active_schedule_ids = [schedule.id for schedule in active_schedules]

    # Получаем логи только для активных расписаний
    logs, total_logs = db_l.get_active_logs_paginated(active_schedule_ids, page=page, per_page=per_page)

    logs_data = [{
        "schedule_id": log.schedule_id,
        "response": log.response,
        "timestamp": log.timestamp
    } for log in logs]

    return jsonify(logs=logs_data, total_logs=total_logs, page=page, per_page=per_page), 200

# Получение логов по schedule_id с пагинацией
@request_log_bp.route('/logs/<int:schedule_id>', methods=['GET'])
@jwt_required()
def get_logs_by_schedule_id(schedule_id):
    from app.database.request_log_manager import RequestLogManager
    db = RequestLogManager()

    # Параметры пагинации
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)

    logs, total_logs = db.get_logs_by_schedule_paginated(schedule_id=schedule_id, page=page, per_page=per_page)

    logs_data = [{
        "schedule_id": log.schedule_id,
        "response": log.response,
        "timestamp": log.timestamp
    } for log in logs]

    return jsonify(logs=logs_data, total_logs=total_logs, page=page, per_page=per_page), 200
