from flask import Blueprint
from flask_jwt_extended import create_access_token
from flask import render_template, jsonify, request, session



login_bp = Blueprint('login', __name__)


# Основная страница
@login_bp.route('/')
def index():
    return render_template('login.html')


# Маршрут для входа (авторизации)
@login_bp.route('/auth', methods=['POST'])
def auth():
    from app.database.user_manager import UserManager
    # Создаем экземпляр менеджера базы данных
    db = UserManager()
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    # Проверяем пользователя в базе данных
    if not db.user_exists(username) or not db.check_password(username, password):
        return jsonify({"msg": "Bad username or password"}), 401

    # Генерируем JWT токен
    access_token = create_access_token(identity=username)
    session['access_token'] = access_token  # Сохраняем токен в сессии
    return jsonify(access_token=access_token)


# Маршрут для страницы входа
@login_bp.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

# Выход из системы
@login_bp.route('/logout')
def logout():
    return jsonify({"msg": "Logout successful"}), 200
