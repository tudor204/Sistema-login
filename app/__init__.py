import os
from dotenv import load_dotenv
from flask import Flask

load_dotenv()  # Carga variables del .env

app= Flask(__name__)
app.run(debug=True)
app.secret_key = os.urandom(24)  # Para usar flash()

from app.routes import *