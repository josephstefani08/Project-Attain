from flask import Flask
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
import os

# Configure application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'x1exddEx92D+x1cxaax7fx90cx9dxa4x89xfaSxddx07qxe5f'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attain.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')
# app.config['MAIL_USERNAME'] = 'noreplyattain@gmail.com'
# app.config['MAIL_PASSWORD'] = 'AttainProject'

mail = Mail(app)

from attain import routes
