from apscheduler.schedulers.background import BackgroundScheduler
import requests
import datetime
from db_manager import DatabaseManager


db = DatabaseManager()

# Создаем таблицы
db.create_tables()

# Функция для выполнения запроса по расписанию
def execute_schedule(schedule_id):
    schedule = db.get_schedule_by_id(schedule_id)
    if not schedule:
        return

    try:
        if schedule.method == 'GET':
            response = requests.get(schedule.url)
        elif schedule.method == 'POST':
            response = requests.post(schedule.url, data=schedule.data)
        
        # Логируем результат запроса
        log = db.add_request_log(schedule_id=schedule.id, response=response.text, timestamp=datetime.utcnow())
        db.session.add(log)
        db.session.commit()

        # Обновляем время последнего выполнения
        schedule.last_run = datetime.utcnow()
        db.session.commit()

    except Exception as e:
        print(f"Error executing schedule {schedule_id}: {e}")

# Запуск планировщика
scheduler = BackgroundScheduler()

def schedule_jobs():
    schedules = db.get_schedules()
    for schedule in schedules:
        interval_in_seconds = schedule.interval * 60
        scheduler.add_job(execute_schedule, 'interval', seconds=interval_in_seconds, args=[schedule.id])

scheduler.start()

# При инициализации приложения, загружаем расписания
@app.before_first_request
def initialize_scheduler():
    schedule_jobs()
