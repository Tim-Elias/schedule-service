import uuid
from flask_restx import abort, ValidationError

# Функция для валидации UUID в моделях
def validate_uuid(value):
    try:
        uuid.UUID(value)
    except ValueError:
        raise ValidationError(f"{value} is not a valid UUID")

# Декоратор для валидации UUID в параметрах URL
def validate_uuid_param(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        schedule_id = kwargs.get('schedule_id')
        if schedule_id:
            try:
                uuid.UUID(schedule_id)
            except ValueError:
                abort(400, f"{schedule_id} is not a valid UUID")
        return f(*args, **kwargs)
    return decorated_function
