from flask import jsonify, request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from app.scheduler.scheduler import execute_schedule, scheduler
from app.scheduler.scheduler_actions import activate_scheduler
import logging
from datetime import datetime
from app.validators import validate_uuid, validate_uuid_param
from flask_cors import cross_origin

schedule_actions_ns = Namespace('schedule', description='Schedule Actions operations')

app_logger = logging.getLogger('app_logger')


# Определение модели для добавления расписания
new_schedule_model = schedule_actions_ns.model('AddSchedule', {
    'method': fields.String(required=True, description='HTTP Method'),
    'url': fields.String(required=True, description='URL for the schedule'),
    'schedule_type': fields.String(required=True, description='Type of schedule'),
    'data': fields.Raw(description='Data for POST requests'),
    'interval': fields.Integer(description='Interval in minutes for interval schedule'),
    'time_of_day': fields.String(description='Time of day for daily schedule (HH:MM)')
})

response_model = schedule_actions_ns.model('ActionResponse', {
    'message': fields.String(required=True, description='Is the action successful'),
    'id': fields.String(required=False, description='Schedule ID', validate=validate_uuid)
})


@schedule_actions_ns.route('/')
class ScheduleCreate(Resource):
    @cross_origin()
    @schedule_actions_ns.expect(new_schedule_model)
    @schedule_actions_ns.marshal_with(response_model)
    @jwt_required()
    def post(self):
        from app.database.schedule_manager import ScheduleManager
        db = ScheduleManager()
        try:
            data = request.json
            method = data.get('method')
            url = data.get('url')
            schedule_type = data.get('schedule_type')  # Новый параметр типа расписания
            post_data = data.get('data', None)  # Данные для POST-запроса (если это POST)

            app_logger.info(f"Received schedule data: method={method}, url={url}, schedule_type={schedule_type}, post_data={post_data}")

            # Проверяем наличие обязательных полей
            if not method or not url or not schedule_type:
                app_logger.error("Missing required fields: Method, URL, and Schedule Type are required")
                return {"message": "Method, URL, and schedule_type are required"}, 400

            # Разные обработки в зависимости от типа расписания
            if schedule_type == 'interval':
                interval = data.get('interval')  # Интервал в минутах
                if not interval:
                    app_logger.error("Missing interval for interval schedule")
                    return {"message": "Interval is required for interval schedule"}, 400

                interval_in_seconds = int(interval) * 60
                app_logger.debug(f"Converted interval to seconds: {interval_in_seconds}")

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
                app_logger.info(f"New interval schedule added to database with ID: {new_schedule['id']}")

                # Добавляем задачу в планировщик по интервалу
                scheduler.add_job(
                    execute_schedule, 
                    'interval', 
                    seconds=interval_in_seconds, 
                    args=[new_schedule['id']], 
                    id=f"schedule_{new_schedule['id']}"
                )
                # Запускаем задачу немедленно после создания
                execute_schedule(new_schedule[id])
                app_logger.info(f"Scheduled interval job created and executed for schedule ID: {new_schedule['id']}")

            elif schedule_type == 'daily':
                time_of_day = data.get('time_of_day')  # Время выполнения задачи
                if not time_of_day:
                    app_logger.error("Missing time_of_day for daily schedule")
                    return {"message": "Time of day is required for daily schedule"}, 400

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
                app_logger.info(f"New daily schedule added to database with ID: {new_schedule['id']}")
                # Добавляем задачу в планировщик для ежедневного выполнения
                scheduler.add_job(
                    execute_schedule, 
                    'cron', 
                    hour=time_of_day_obj.hour, 
                    minute=time_of_day_obj.minute, 
                    second=0,
                    args=[new_schedule['id']],
                    id=f"schedule_{new_schedule['id']}"
                )
                app_logger.info(f"Scheduled daily job created for schedule ID: {new_schedule['id']}")
            else:
                app_logger.error("Invalid schedule type provided")
                return {"message": "Invalid schedule type"}, 400
            # Логируем успешное выполнение задачи
            app_logger.info(f"Scheduled job executed for schedule ID: {new_schedule['id']}")
            return {"message": "Schedule created and task added successfully", "schedule_id": f"{new_schedule['id']}"}, 201
        except Exception as e:
            # Логируем ошибку и возвращаем информацию для отладки
            app_logger.error(f"Error adding schedule: {e}")
            return {"message": "Failed to create schedule", "error": str(e)}, 500


edit_schedule_model = schedule_actions_ns.model('EditSchedule', {
    'method': fields.String(required=False, description='HTTP Method'),
    'url': fields.String(required=False, description='URL for the schedule'),
    'schedule_type': fields.String(required=False, description='Type of schedule'),
    'data': fields.Raw(required=False, description='Data for POST requests'),
    'interval': fields.Integer(required=False, description='Interval in minutes for interval schedule'),
    'time_of_day': fields.String(required=False, description='Time of day for daily schedule (HH:MM)'),
    'is_active': fields.Boolean(required=False, description='Is the schedule')
})



@schedule_actions_ns.route('/<string:id>/edit')
class ScheduleEdite(Resource):
    @cross_origin()
    @schedule_actions_ns.expect(edit_schedule_model)
    @schedule_actions_ns.marshal_with(response_model)
    @validate_uuid_param  # Используем декоратор для проверки валидности schedule_id
    @jwt_required()
    def post(self, id):
        from app.database.schedule_manager import ScheduleManager
        db = ScheduleManager()
        data = request.json
        app_logger.info(f"Received data {data}.")
        # Инициализируем словарь для хранения сообщений
        messages = []

        # Формируем словарь фильтров
        method = data.get('method')
        url = data.get('url')
        post_data = data.get('data')
        schedule_type = data.get('schedule_type')
        is_active = data.get('is_active')
        time_of_day = data.get('time_of_day')
        interval = data.get('interval')
        
        # Получаем старый график
        old_schedule = db.get_schedule_by_id(id)

        # Проверяем, активен ли старый график
        if old_schedule['is_active']:
            job_id = f"schedule_{id}"
            scheduler.remove_job(job_id)
            messages.append(f"Job {job_id} removed successfully.")
            app_logger.info(f"Job {job_id} removed successfully.")

        # Обновляем запрос, если есть необходимые данные
        if url or post_data or method:
            try:
                new_request = db.update_schedule_request(id=id, method=method, url=url, post_data=post_data)
                messages.append(f"Schedule {id} request updated successfully.")
                app_logger.info(f"Schedule {id} request updated successfully.")
            except Exception as e:
                messages.append(f"Failed to update schedule {id} request.")
                app_logger.error(f"Error updating schedule {id} request: {e}")

        # Обновляем время, если есть необходимые данные
        if schedule_type or interval or time_of_day:
            try:
                new_time = db.update_schedule_time(id=id, schedule_type=schedule_type, interval=interval, time_of_day=time_of_day)
                messages.append(f"Schedule {id} time updated successfully.")
                app_logger.info(f"Schedule {id} time updated successfully.")
            except Exception as e:
                messages.append(f"Failed to update schedule {id} time.")
                app_logger.error(f"Error updating schedule {id} time: {e}")

        # Обрабатываем активность расписания
        if is_active is not None:
            try:
                if is_active:
                    db.activate_schedule(id)
                    activate_scheduler(id)
                    app_logger.info(f"Schedule {id} activated")
                    messages.append(f"Schedule {id} activated successfully.")
                else:
                    db.deactivate_schedule(id)
                    app_logger.info(f"Schedule {id} deactivated")
                    messages.append(f"Schedule {id} deactivated successfully.")
            except Exception as e:
                messages.append(f"Failed to change activity status for schedule {id}.")
                app_logger.error(f"Error changing activity status for schedule {id}: {e}")

        else:
            if old_schedule['is_active']:
                try:
                    activate_scheduler(id)
                    messages.append(f"Scheduler for Schedule {id} activated successfully.")
                    app_logger.info(f"Scheduler for Schedule {id} activated successfully.")
                except Exception as e:
                    messages.append(f"Failed to activate scheduler for schedule {id}.")
                    app_logger.error(f"Error activating scheduler for schedule {id}: {e}")
        
        # Возвращаем сообщения об обновлениях
        return {"message": messages}, 200  # Возвращаем статус 200 и сообщения



@schedule_actions_ns.route('/<string:id>/delete')
class ScheduleDelete(Resource):
    @schedule_actions_ns.marshal_with(response_model)
    @cross_origin()
    @jwt_required()
    @validate_uuid_param  # Используем декоратор для проверки валидности schedule_i
    def delete(self, id):
        from app.database.schedule_manager import ScheduleManager
        db = ScheduleManager()
        schedule = db.delete_schedule(id)
        if schedule:
            job_id = f"schedule_{id}"
            scheduler.remove_job(job_id)
            return jsonify({"message": "Schedule deleted successfully"}), 200
        return jsonify({"message": "Error deleting schedule"}), 500

