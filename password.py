from app.database.user_manager import UserManager
import os
from dotenv import load_dotenv
from app import create_app

load_dotenv()
db = UserManager()
port = os.getenv('PORT')

password=os.getenv('PASSWORD')
username=os.getenv('LOGIN')
app = create_app()
app.run(debug=True, host='0.0.0.0', port=port)
db.add_user_password(username, password)
#email='mintbunny.eng@gmail.com'
#db.add_user_google(email, auth_type='google')