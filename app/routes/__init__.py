from flask_restx import Api
from .login_routes import login_ns
from .schedules_routes import schedules_ns
from .request_log_routes import request_logs_ns
from .schedule_action_routes import schedule_actions_ns
from .schedule_details_routes import schedule_details_ns
from .log_route import log_ns

def register_routes(api: Api):
    api.add_namespace(schedules_ns)
    api.add_namespace(schedule_actions_ns)
    api.add_namespace(schedule_details_ns)
    api.add_namespace(request_logs_ns)
    api.add_namespace(login_ns)
    api.add_namespace(log_ns)
