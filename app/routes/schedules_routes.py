from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
import logging
from flask_cors import cross_origin

# Настройка логирования
app_logger = logging.getLogger('app_logger')

schedules_ns = Namespace('schedules', description='All Schedules operations')

# Определение модели для ответа о расписании
schedule_response_model = schedules_ns.model('ScheduleResponse', {
    'id': fields.String(required=True, description='Schedule ID'),
    'method': fields.String(required=True, description='HTTP Method'),
    'url': fields.String(required=True, description='URL for the schedule'),
    'schedule_type': fields.String(required=True, description='Type of schedule'),
    'data': fields.Raw(description='Data for POST requests'),
    'last_run': fields.String(description='Last Run Time'),
    'is_active': fields.Boolean(required=True, description='Is Schedule Active'),
    'interval': fields.Integer(description='Interval in minutes for interval schedule'),
    'time_of_day': fields.String(description='Time of day for daily schedule (HH:MM)')
})

get_schedule_model = schedules_ns.model('GetSchedules', {
    'offset': fields.Integer(required=False, description='Number of records to skip'),
    'limit': fields.Integer(required=False, description='Number of records to return'),
    'sort_by': fields.String(required=False, description='Field to sort by'),
    'sort_order': fields.String(required=False, description='Sort order: asc or desc', enum=['asc', 'desc']),
    'id': fields.String(required=False, description='Schedule ID'),
    'method': fields.String(required=False, description='HTTP Method'),
    'url': fields.String(required=False, description='URL for the schedule'),
    'schedule_type': fields.String(required=False, description='Type of schedule'),
    'data': fields.Raw(required=False, description='Data for POST requests'),
    'last_run': fields.String(required=False, description='Last Run Time'),
    'is_active': fields.Boolean(required=False, description='Is Schedule Active'),
    'interval': fields.Integer(required=False, description='Interval in minutes for interval schedule'),
    'time_of_day': fields.String(required=False, description='Time of day for daily schedule (HH:MM)')
})

@schedules_ns.route('/')
class AllSchedulesResource(Resource):
    @cross_origin()
    @jwt_required()
    @schedules_ns.expect(get_schedule_model)
    @schedules_ns.marshal_list_with(schedule_response_model)
    def get(self):
        app_logger.info('Получен запрос на получение расписаний.')
        from app.database.schedule_manager import ScheduleManager
        db = ScheduleManager()
        try:
            app_logger.debug('Пытаемся извлечь параметры запроса.')
            # Получаем параметры из строки запроса (query parameters)
            offset = request.args.get('offset', default=0, type=int)  # По умолчанию 0
            limit = request.args.get('limit', default=10, type=int)    # По умолчанию 10
            app_logger.debug(f'Параметры запроса - offset: {offset}, limit: {limit}')
            sort_by = request.args.get('sort_by', None)  # Поле для сортировки
            sort_order = request.args.get('sort_order', 'asc')  # Порядок сортировки
            app_logger.info(f'Получены данные: {sort_by}, {sort_order}.')
            # Формируем словарь фильтров
            filters = {
                'id': request.args.get('id'),
                'method': request.args.get('method'),
                'url': request.args.get('url'),
                'schedule_type': request.args.get('schedule_type'),
                'data': request.args.get('data'),
                'last_run': request.args.get('last_run'),
                'is_active': request.args.get('is_active', type=bool),
                'time_of_day': request.args.get('time_of_day'),
                'interval': request.args.get('interval', type=int)
            }

            # Убедитесь, что ключи 'offset' и 'limit' не попадают в фильтры
            filters = {k: v for k, v in filters.items() if k not in ['offset', 'limit']}
            app_logger.info(f'Получен фильтр: {filters}.')
            app_logger.debug(f'Вызов get_all_schedules_filtered с параметрами: offset={offset}, limit={limit}, sort_by={sort_by}, sort_order={sort_order}, filters={filters}')
            schedules = db.get_all_schedules_filtered(offset, limit, sort_by, sort_order, **filters)
            app_logger.info('Запрос на получение расписаний успешно выполнен.')
            return schedules, 200
        except Exception as e:
            app_logger.error(f'Произошла ошибка при обработке запроса: {str(e)}')
            return {"error": f"Произошла ошибка: {str(e)}"}, 500

