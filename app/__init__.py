import os
from dotenv import load_dotenv
from flask import Flask, request, session
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth
from flask_babel import Babel, gettext as _

load_dotenv()


app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

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
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# Configuración de Flask-Babel para internacionalización
app.config['BABEL_DEFAULT_LOCALE'] = 'es'  # idioma por defecto
app.config['BABEL_SUPPORTED_LOCALES'] = ['es', 'en', 'fr']  # idiomas disponibles



def get_locale():
    user_lang = session.get('user_lang')
    supported = ['es', 'en', 'fr']  # o usa app.config['BABEL_SUPPORTED_LOCALES']
    if user_lang in supported:
        return user_lang
    return request.accept_languages.best_match(supported)
babel = Babel(app, locale_selector=get_locale)

from app.models.LoginGoogleModel import User

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

from app.controllers import (
    LoginGoogleController,
    DashboardController,
    IndexController,
    MyfoodsController,
    ProgressController,
    SearchFoodController,
    UsersController,
    SettingsController,
    ActivityController,
)
