# schedule-service
schedule-service
# Устанавливает нового админа
python password.py 
# Устанавливает все миграции
alembic upgrade head 
# Устанавливает все зависимости
pip install -r ./app/requirements.txt
