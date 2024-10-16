from flask import Blueprint, jsonify
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required
from request_logger import RequestLogHandler
from flask_cors import cross_origin

log_ns = Namespace('logs', description='Logs related operations')

@log_ns.route('/')
class LogResource(Resource):
    @cross_origin()
    @jwt_required()  # Защита маршрута JWT
    def get(self):
        logs = RequestLogHandler.get_logs()
        return logs, 200

