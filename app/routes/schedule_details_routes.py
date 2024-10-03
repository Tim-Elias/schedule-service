from flask import Blueprint
from flask_jwt_extended import jwt_required
from flask import render_template, jsonify, request, redirect, url_for


schedule_details_bp = Blueprint('schedule_details', __name__)



# Маршрут деталей о расписании
@schedule_details_bp.route('/schedule_details', methods=['GET'])
def schedule_details():
    from app.database.schedule_manager import ScheduleManager
    db_s = ScheduleManager()
    from app.database.request_log_manager import RequestLogManager
    db_l = RequestLogManager()
    
    # Параметры пагинации
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    
    schedule_id = request.args.get('id', type=int)
    if not schedule_id:
        return redirect(url_for('get_all_schedules'))
    
    schedule = db_s.get_schedule_by_id(schedule_id)
    logs, total_logs = db_l.get_logs_by_schedule_paginated(schedule_id, page=page, per_page=per_page)
    
    return render_template('schedule_details.html', 
                           schedule=schedule, 
                           logs=logs,  # Список логов на текущей странице
                           page=page, 
                           per_page=per_page, 
                           total_logs=total_logs)  # Общее количество логов для пагинации



# Пример функции обновления расписания
@schedule_details_bp.route('/schedule/<int:schedule_id>', methods=['PUT'])
@jwt_required()
def update_schedule(schedule_id):
    data = request.json
    from app.database.schedule_manager import ScheduleManager
    db_s = ScheduleManager()
    # Логика поиска расписания в базе данных
    schedule = db_s.get_schedule_by_id(schedule_id)
    
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
    db_s.update_schedule(schedule)
    
    return jsonify({'message': 'Schedule updated successfully'}), 200