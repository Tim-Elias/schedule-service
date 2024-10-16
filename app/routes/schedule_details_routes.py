from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from app.validators import validate_uuid, validate_uuid_param
from flask_cors import cross_origin

schedule_details_ns = Namespace('schedule', description='Schedule Details operations')

# Определение модели для расписания
schedule_detail_model = schedule_details_ns.model('ScheduleDetail', {
    'id': fields.String(required=True, description='Schedule ID', validate=validate_uuid),
    'method': fields.String(required=True, description='HTTP Method'),
    'url': fields.String(required=True, description='URL for the schedule'),
    'schedule_type': fields.String(required=True, description='Type of schedule'),
    'data': fields.Raw(description='Data for POST requests'),
    'last_run': fields.String(description='Last Run Time'),
    'is_active': fields.Boolean(required=True, description='Is Schedule Active'),
    'interval': fields.Integer(description='Interval in minutes for interval schedule'),
    'time_of_day': fields.String(description='Time of day for daily schedule (HH:MM)')
})

@schedule_details_ns.route('/<string:schedule_id>/view')
class ScheduleDetailResource(Resource):
    @cross_origin()
    @jwt_required()
    @schedule_details_ns.marshal_with(schedule_detail_model)
    @validate_uuid_param  # Используем декоратор для проверки валидности schedule_i
    def get(self, schedule_id):
        from app.database.schedule_manager import ScheduleManager
        db = ScheduleManager()
        schedule = db.get_schedule_by_id(schedule_id)
        if schedule:
            return schedule, 200
        return {'msg': 'Schedule not found'}, 404


