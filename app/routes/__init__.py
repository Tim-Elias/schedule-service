from flask import Flask
from .login_routes import login_bp
from .google_auth_route import google_auth_bp
from .active_schedules_routes import active_schedules_bp  # Если у вас есть другие маршруты
from .all_schedules_routes import all_schedules_bp
from .request_log_routes import request_log_bp
from .schedule_action_routes import schedule_action_bp
from .schedule_details_routes import schedule_details_bp

__all__ = ['login_bp', 'all_schedules_bp', 'active_schedules_bp', 'request_log_bp', 'schedule_action_bp', 'schedule_details_bp']

def register_routes(app: Flask):
    app.register_blueprint(login_bp)  
    #app.register_blueprint(google_auth_bp)  
    app.register_blueprint(active_schedules_bp)
    app.register_blueprint(all_schedules_bp)
    app.register_blueprint(request_log_bp)
    app.register_blueprint(schedule_action_bp)
    app.register_blueprint(schedule_details_bp)
