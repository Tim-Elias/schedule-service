from db_manager import DatabaseManager

db = DatabaseManager()

# Создаем таблицы
db.create_tables()

password='qweasdzxc'
username='123'
db.add_user(username, password)