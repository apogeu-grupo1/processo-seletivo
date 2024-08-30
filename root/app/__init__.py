from flask import Flask
from flask_bcrypt import Bcrypt
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
bcrypt = Bcrypt(app)

from app.routes import *  # Importa todas as rotas definidas em app/routes/__init__.py