# app/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import logging
import requests

 # Импорт сессии для работы с БД

# Инициализация планировщика
scheduler = BackgroundScheduler()

# Функция для выполнения расписания
def execute_schedule(schedule_id):
    from app.database.schedule_manager import ScheduleManager
    from app.database.request_log_manager import RequestLogManager
    logging.debug(f"Executing schedule with ID: {schedule_id}")
    db_s = ScheduleManager()  # Инициализируем менеджера базы данных
    db_l = RequestLogManager()
    schedule = db_s.get_schedule_by_id(schedule_id)
    if not schedule:
        logging.error('No schedule found with the given ID')
        return

    logging.debug(f"Schedule details: {schedule}")

    try:
        method = schedule.method
        url = schedule.url
        data = schedule.data if schedule.method == 'POST' else None
        
        if method == 'GET':
            response = requests.get(url)
        elif method == 'POST':
            response = requests.post(url, data=data)
        
        logging.debug(f"Response: {response.text}")
        
        db_l.add_request_log(
            schedule_id=schedule.id,
            response=response.text
        )
        
        # Обновляем время последнего выполнения
        schedule.last_run = datetime.utcnow()
        db_s.update_schedule(schedule)
        logging.info(f"Schedule {schedule.id} successfully executed at {schedule.last_run}")

    except Exception as e:
        logging.error(f"Error during request: {e}")

# Функция для инициализации расписаний в планировщике
def initialize_scheduler():
    from app.database.schedule_manager import ScheduleManager
    db_manager = ScheduleManager()
    schedules = db_manager.get_active_schedules()
    for schedule in schedules:
        if schedule.schedule_type == 'interval':
            interval_in_seconds = schedule.interval * 60
            scheduler.add_job(execute_schedule, 'interval', seconds=interval_in_seconds, args=[schedule.id])
        elif schedule.schedule_type == 'daily':
            run_time = schedule.time_of_day
            scheduler.add_job(
                execute_schedule,
                'cron',
                hour=run_time.hour, 
                minute=run_time.minute, 
                second=0,
                args=[schedule.id]
            )

# Запуск планировщика
def start_scheduler():
    scheduler.start()

# Остановка планировщика
def stop_scheduler():
    scheduler.shutdown()

