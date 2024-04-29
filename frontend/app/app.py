from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)

app.config['SECRET_KEY'] = 'rsww-projekt-klucz'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db = SQLAlchemy(app)
from models import create
create()

from main_pages import mainpages as main_blueprint
app.register_blueprint(main_blueprint)

from api import api as api_blueprint
app.register_blueprint(api_blueprint)

from auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)
