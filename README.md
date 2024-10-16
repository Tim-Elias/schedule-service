# schedule-service
schedule-service
# Первый запуск и инициализация базы данных
python run.py
# Устанавливает нового админа
python password.py 
# Устанавливает все миграции
alembic upgrade head 
# Устанавливает все зависимости
pip install -r requirements.txt
