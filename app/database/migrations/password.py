
def admin(password, username):
    from app.database.user_manager import UserManager
    db = UserManager()
    

    if db.user_exists(username):
        db.delete_user_by_username(username)

    db.add_user_password(username, password, auth_type='password')
    print('New admin added successfully')