from app.scheduler.scheduler import scheduler, execute_schedule
import logging

app_logger = logging.getLogger('app_logger')


def activate_scheduler(id):
    from app.database.schedule_manager import ScheduleManager
    db = ScheduleManager()
    schedule=db.get_schedule_by_id(id)
    if schedule['schedule_type'] == 'interval':
        # Преобразуем интервал в секунды для интервала
        interval_in_seconds = int(schedule['interval']) * 60
        # Добавляем задачу в планировщик
        scheduler.add_job(
            execute_schedule, 
            'interval', 
            seconds=interval_in_seconds, 
            args=[schedule['id']], 
            id=f"schedule_{schedule['id']}"
        )
        # Немедленный запуск задачи
        execute_schedule(schedule['id'])
        app_logger.info(f"Scheduled job created and executed for schedule ID: {schedule['id']} (interval)")
    elif schedule['schedule_type'] == 'daily':
        # Преобразуем время в строковый формат для планировщика
        schedule_time = schedule['time_of_day'].strftime('%H:%M:%S')
        # Добавляем задачу в планировщик
        scheduler.add_job(
            execute_schedule, 
            'cron', 
            hour=schedule_time.hour,
            minute=schedule_time.minute, 
            second=schedule_time.second,
            args=[schedule['id']], 
            id=f"schedule_{schedule['id']}"
        )
        app_logger.info(f"Scheduled job created for schedule ID: {schedule['id']} (daily at {schedule['time_of_day']})")

