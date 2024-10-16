from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
import logging
from app.validators import validate_uuid, validate_uuid_param
from flask_cors import cross_origin

# Настройка логирования
app_logger = logging.getLogger('app_logger')

request_logs_ns = Namespace('request_logs', description='Request Logs operations')


# Определение модели для ответа о логах
# Добавляем валидатор в модель
log_response_model = request_logs_ns.model('LogResponse', {
    'id': fields.String(required=True, description='Log ID', validate=validate_uuid),
    'schedule_id': fields.String(required=True, description='Schedule ID', validate=validate_uuid),
    'response': fields.String(required=True, description='Response from the server'),
    'timestamp': fields.DateTime(required=True, description='Timestamp of the request'),
    'status_code': fields.Integer(required=True, description='HTTP Status Code')
})

get_logs_model = request_logs_ns.model('GetLogs', {
    'offset': fields.Integer(required=False, description='Number of records to skip'),
    'limit': fields.Integer(required=False, description='Number of records to return'),
    'sort_by': fields.String(required=False, description='Field to sort by'),
    'sort_order': fields.String(required=False, description='Sort order: asc or desc', enum=['asc', 'desc']),
    'id': fields.String(required=False, description='HTTP method to filter by', validate=validate_uuid),
    'schedule_id': fields.String(required=False, description='Schedule_id to filter by', validate=validate_uuid),
    'response': fields.String(required=False, description='Response to filter by'),
    'timestamp': fields.DateTime(required=False, description='Date to filter by'),
    'status_code': fields.Integer(required=False, description='Status_code to filter by')
})

get_logs_by_schedule_model = request_logs_ns.model('GetLogsBySchedule', {
    'offset': fields.Integer(required=False, description='Number of records to skip'),
    'limit': fields.Integer(required=False, description='Number of records to return')
})

@request_logs_ns.route('/')
class RequestLogsResource(Resource):
    @cross_origin()
    @jwt_required()
    @request_logs_ns.expect(get_logs_model)
    @request_logs_ns.marshal_list_with(log_response_model)
    def get(self):
        from app.database.request_log_manager import RequestLogManager
        db = RequestLogManager()
        """
        Получить логи запросов с возможностью пагинации и фильтрации.
        """
        
        offset = request.args.get('offset', 0)  # По умолчанию 0
        limit = request.args.get('limit', 10)    # По умолчанию 10
        app_logger.debug(f'Параметры запроса - offset: {offset}, limit: {limit}')
        sort_by = request.args.get('sort_by', None)  # Поле для сортировки, по умолчанию timestamp
        sort_order = request.args.get('sort_order', 'asc')   # Порядок сортировки, по умолчанию asc
        app_logger.info(f'Получены данные: {sort_by}, {sort_order}.')
        # Получаем фильтры
        log_id = request.args.get('id')  # Вытаскиваем id фильтр
        schedule_id = request.args.get('schedule_id')  # Вытаскиваем schedule_id фильтр
        response = request.args.get('response')  # Вытаскиваем response фильтр
        timestamp = request.args.get('timestamp')  # Вытаскиваем timestamp фильтр

        # Формируем словарь фильтров
        filters = {
            'id': log_id,
            'schedule_id': schedule_id,
            'response': response,
            'timestamp': timestamp
        }
        app_logger.info(f'Получен фильтр: {filters}.')
        # Вызываем вашу функцию менеджера
        app_logger.debug(f'Вызов get_all_schedules_filtered с параметрами: offset={offset}, limit={limit}, sort_by={sort_by}, sort_order={sort_order}, filters={filters}')
        logs = db.get_request_logs_filtered(offset=offset, limit=limit, sort_by=sort_by, sort_order=sort_order, **filters)

        return logs, 200



@request_logs_ns.route('/<string:schedule_id>')
class RequestLogResource(Resource):
    @cross_origin()
    @jwt_required()
    @request_logs_ns.expect(get_logs_by_schedule_model)
    @request_logs_ns.marshal_with(log_response_model)
    @validate_uuid_param  # Используем декоратор для проверки валидности schedule_id
    def get(self, schedule_id):
        # Валидация UUID
        validate_uuid(schedule_id)  # Проверяем переданный в путь schedule_id
        from app.database.request_log_manager import RequestLogManager
        db = RequestLogManager()
        
        offset=request.args.get('offset', 0)
        limit = request.args.get('limit', 10)
        app_logger.debug(f'Параметры запроса - offset: {offset}, limit: {limit}')
        logs = db.get_logs_by_schedule(schedule_id, offset, limit)
        return logs, 200

