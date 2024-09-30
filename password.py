from app.database.user_manager import UserManager
import os
from dotenv import load_dotenv



load_dotenv()
db = UserManager()


password=os.getenv('PASSWORD')
username=os.getenv('LOGIN')
#db.add_user_password(username, password)
email='mintbunny.eng@gmail.com'
db.add_user_google(email, auth_type='google')