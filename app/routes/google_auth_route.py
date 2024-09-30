import logging
import os
import requests
from flask import Blueprint, jsonify, request, url_for, session, redirect, render_template
from authlib.jose import jwt
from flask_jwt_extended import create_access_token

google_auth_bp = Blueprint('google_auth', __name__)


@google_auth_bp.route('/auth_page')
def auth_page():
    token = request.args.get('token')
    return render_template('auth_page.html', token=token)


@google_auth_bp.route('/auth/google')
def auth_google():
    redirect_uri = url_for('google_auth.auth_callback', _external=True)
    print("Redirect URI:", redirect_uri)  # Для отладки
    return google_auth_bp.oauth.authorize_redirect(redirect_uri)

@google_auth_bp.route('/auth/callback')
def auth_callback():
    from app.database.user_manager import UserManager
    db = UserManager()
    code = request.args.get('code')
    #state = request.args.get('state')
    
    if code:
        redirect_uri = url_for('google_auth.auth_callback', _external=True)
        token_response = requests.post(
            'https://oauth2.googleapis.com/token',
            data={
                'code': code,
                'client_id': os.getenv('GOOGLE_CLIENT_ID'),
                'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
                'redirect_uri': redirect_uri,
                'grant_type': 'authorization_code',
            },
        )
        token_json = token_response.json()
        access_token = token_json.get('access_token')

        if access_token:
            # Получаем информацию о пользователе
            user_info_response = requests.get(
                'https://www.googleapis.com/oauth2/v3/userinfo',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            user_info = user_info_response.json()
            sub = user_info.get('sub')
            username=user_info.get('email')
            if  not db.google_user_exists(sub):
                db.add_user_google(username,sub)
            # Генерируем JWT токен
            access_token = create_access_token(identity=username)
            session['access_token'] = access_token  # Сохраняем токен в сессии
            #return jsonify(access_token=access_token), 200
            return redirect(url_for('google_auth.auth_page', token=access_token))
            
        logging.error(f"Token exchange failed: {token_response.json()}")
        return jsonify({"msg": "Token exchange failed"}), 400
    logging.error("No code received from Google")
    return jsonify({"msg": "No code provided"}), 400



# Верификация гугл токена
def verify_google_token(id_token):
    jwks_url = "https://www.googleapis.com/oauth2/v3/certs"
    jwks = requests.get(jwks_url).json()

    try:
        claims = jwt.decode(id_token, jwks)
        claims.validate()
        return claims
    except Exception as e:
        logging.error(f"Token verification failed: {str(e)}")
        raise ValueError("Token verification failed")

