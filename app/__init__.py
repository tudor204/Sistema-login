import os
from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth

load_dotenv()  # Carga variables de entorno del archivo .env

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'una_clave_fija_para_dev')


# Configura Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configura OAuth con Authlib
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_OAUTH_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_OAUTH_CLIENT_SECRET'),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',  # Endpoint para info usuario
    client_kwargs={'scope': 'openid email profile'},
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',  # <-- MUY IMPORTANTE
)

# Importa tu modelo User para Flask-Login
from app.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)  # Aquí debes tener tu método para obtener usuario por ID

# Importa rutas al final para evitar referencias circulares
from app import routes
