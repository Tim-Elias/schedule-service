from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import requests
import json
import logging

# Инициализация планировщика
scheduler = BackgroundScheduler()
# Настройка логирования
app_logger = logging.getLogger('app_logger')

# Функция для выполнения расписания
def execute_schedule(schedule_id):
    from app.database.schedule_manager import ScheduleManager
    from app.database.request_log_manager import RequestLogManager

    app_logger.debug(f"Executing schedule with ID: {schedule_id}")

    # Инициализация менеджера базы данных
    db_s = ScheduleManager()
    db_l = RequestLogManager()

    # Получение расписания по ID
    app_logger.debug(f"Attempting to retrieve schedule with ID: {schedule_id}")
    schedule = db_s.get_schedule_by_id(schedule_id)
    
    if not schedule:
        app_logger.error(f"No schedule found with ID: {schedule_id}")
        return

    app_logger.debug(f"Schedule retrieved: {schedule}")

    try:
        # Получение метода и URL из расписания
        method = schedule['method']
        url = schedule['url']
        data = schedule['data'] if method == 'POST' else None
        
        # Логирование подготовленного запроса
        app_logger.debug(f"Prepared request - Method: {method}, URL: {url}, Data: {data}")

        # Выполнение HTTP-запроса в зависимости от метода
        if method == 'GET':
            response = requests.get(url)
        elif method == 'POST':
            response = requests.post(url, data=json.dumps(data))

        # Логируем полученный ответ от сервера
        app_logger.debug(f"Received response from {url}: Status Code: {response.status_code}, Response Body: {response.text}")

        # Проверяем, является ли ответ корректным JSON
        try:
            json_response = json.loads(response.text)
            app_logger.debug(f"Valid JSON response parsed successfully.")
            # Преобразуем JSON в строку для логирования с корректной кодировкой (без Unicode escape-последовательностей)
            response_to_log = json.dumps(json_response, ensure_ascii=False)
        except json.JSONDecodeError as json_error:
            app_logger.error(f"Failed to parse response as JSON: error: {json_error}")
            response_to_log = response.text  # Логируем оригинальный текст ответа в случае ошибки

        # Логируем перед добавлением записи в базу данных
        app_logger.debug(f"Logging request to DB: schedule_id={schedule['id']}, status_code={response.status_code}")
        
        # Добавляем запись о запросе в лог в базу данных
        db_l.add_request_log(
            schedule_id=schedule['id'],
            response=response_to_log,
            status_code=response.status_code
        )
        app_logger.debug(f"Request log successfully added to the database for schedule ID: {schedule['id']}")

        # Обновляем время последнего выполнения в базе данных
        db_s.update_last_run(schedule['id'], datetime.utcnow())
        app_logger.info(f"Schedule {schedule['id']} successfully executed and last run time updated at {datetime.utcnow()}")

    except Exception as e:
        # Логируем любые ошибки, которые могут возникнуть во время выполнения запроса или обработки данных
        app_logger.error(f"Error occurred during schedule execution: {e}")


# Функция для инициализации расписаний в планировщике
def initialize_scheduler():
    from app.database.schedule_manager import ScheduleManager
    app_logger.debug("Initializing scheduler with active schedules")

    db_manager = ScheduleManager()
    
    try:
        # Получаем все активные расписания
        schedules = db_manager.get_active_schedules()
        app_logger.info(f"Active schedules retrieved: {[schedule['id'] for schedule in schedules]}")

        # Для каждого расписания добавляем задачу в планировщик
        for schedule in schedules:
            if schedule['schedule_type'] == 'interval':
                interval_in_seconds = schedule['interval'] * 60
                app_logger.debug(f"Adding interval schedule: {schedule['id']} with interval {interval_in_seconds} seconds")
                scheduler.add_job(
                    execute_schedule, 
                    'interval', 
                    seconds=interval_in_seconds, 
                    args=[schedule['id']],
                    id=f"schedule_{schedule['id']}"
                )
                execute_schedule(schedule['id'])
            elif schedule['schedule_type'] == 'daily':
                run_time = schedule['time_of_day']
                if isinstance(run_time, str):
                    run_time = datetime.strptime(run_time, '%H:%M:%S').time()
                app_logger.debug(f"Adding daily schedule: {schedule['id']} at {run_time}")
                scheduler.add_job(
                    execute_schedule,
                    'cron',
                    hour=run_time.hour, 
                    minute=run_time.minute, 
                    second=0,
                    args=[schedule['id']],
                    id=f"schedule_{schedule['id']}"
                )
    except Exception as e:
        app_logger.error(f"Error initializing scheduler: {e}")

# Запуск планировщика
def start_scheduler():
    app_logger.info("Starting the scheduler")
    try:
        scheduler.start()
        app_logger.info("Scheduler started successfully")
    except Exception as e:
        app_logger.error(f"Failed to start the scheduler: {e}")

# Остановка планировщика
def stop_scheduler():
    app_logger.info("Stopping the scheduler")
    try:
        scheduler.shutdown()
        app_logger.info("Scheduler stopped successfully")
    except Exception as e:
        app_logger.error(f"Failed to stop the scheduler: {e}")
