from flask import request, jsonify
from flask_restx import Namespace, Resource
from flask_restx import  fields
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, verify_jwt_in_request
from flask_cors import cross_origin


login_ns = Namespace('auth', description='Authentication related operations')

# Определение модели для логина
login_model = login_ns.model('Login', {
    'username': fields.String(required=True, description='Username for login'),
    'password': fields.String(required=True, description='Password for login')
})

# Определение модели для обновления токена
refresh_model = login_ns.model('RefreshToken', {
    'refresh_token': fields.String(required=True, description='Refresh token for renewing access token')
})

response_auth = login_ns.model('Tokens', {
    'access_token': fields.Raw(required=True, description='Access token for user'),
    'refresh_token': fields.Raw(required=True, description='Refresh token for user')
})

@login_ns.route('/')
class Auth(Resource):
    @cross_origin()
    @login_ns.expect(login_model)
    def post(self):
        from app.database.user_manager import UserManager
        db = UserManager()
        username = request.json.get("username", None)
        password = request.json.get("password", None)

        print(username)
        print(password)
        

        if not db.user_exists(username) or not db.check_password(username, password):
            return {"msg": "Bad username or password"}, 401

        # Получаем user_id из базы данных по username
        user_id = db.get_user_id_by_username(username)

        # Генерируем Access и Refresh токены с дополнительной информацией
        additional_claims = {
            "user_id": user_id,
            "username": username
        }

        access_token = create_access_token(identity=additional_claims)
        refresh_token = create_refresh_token(identity=additional_claims)

        print(f"Generated access_token: {access_token}")
        print(f"Generated refresh_token: {refresh_token}")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }, 200

@login_ns.route('/refresh')
class Auth(Resource):
    @cross_origin()
    @login_ns.expect(refresh_model)  # Использование модели для валидации запроса
    def post(self):
        # Получение токена из тела запроса
        refresh_token = request.json.get('refresh_token', None)

        if not refresh_token:
            return jsonify({"msg": "Missing refresh token"}), 400

        try:
            # Явная валидация токена
            verify_jwt_in_request(refresh=True, locations=["json"])
        except Exception as e:
            return jsonify({"msg": str(e)}), 401

        # Получение текущего пользователя
        current_user = get_jwt_identity()

        # Генерация нового access токена
        new_access_token = create_access_token(identity=current_user)
        new_refresh_token = create_refresh_token(identity = current_user)
        return {"access_token": new_access_token,
                        "refresh_token": new_refresh_token
                        }, 200
