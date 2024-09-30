from app.scheduler import execute_schedule, scheduler
from flask import Blueprint
from flask_jwt_extended import jwt_required
from flask import jsonify
import logging


schedule_action_bp = Blueprint('schedule_action', __name__)



# Активация расписания
@schedule_action_bp.route('/schedule/<int:id>/activate', methods=['PATCH'])
@jwt_required()
def activate_schedule(id):
    from app.database.schedule_manager import ScheduleManager
    db = ScheduleManager()
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
@schedule_action_bp.route('/schedule/<int:id>/deactivate', methods=['PATCH'])
@jwt_required()
def deactivate_schedule(id):
    from app.database.schedule_manager import ScheduleManager
    db = ScheduleManager()
    schedule = db.get_schedule_by_id(id)
    if not schedule:
        return jsonify({"message": "Schedule not found"}), 404
    
    schedule.is_active = False
    db.update_schedule(schedule)
    job_id = f"schedule_{id}"
    scheduler.remove_job(job_id)
    return jsonify({"message": "Schedule deactivated"}), 200

