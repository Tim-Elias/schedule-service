from db_manager import DatabaseManager
import os
from dotenv import load_dotenv



load_dotenv()
db = DatabaseManager()

# Создаем таблицы
db.create_tables()

password=os.getenv('PASSWORD')
username=os.getenv('LOGIN')
db.add_user(username, password)