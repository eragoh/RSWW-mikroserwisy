from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import asyncio
import logging
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


db = SQLAlchemy()
app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)

app.config['SECRET_KEY'] = 'rsww-projekt-klucz'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db = SQLAlchemy(app)
from models import create
create()

from api import api as api_blueprint
app.register_blueprint(api_blueprint)

from auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

from reservations import reservations as reservations_blueprint
app.register_blueprint(reservations_blueprint)

from main_pages import mainpages as main_blueprint
app.register_blueprint(main_blueprint)

from activities import activities as activities_blueprint
app.register_blueprint(activities_blueprint)

@app.errorhandler(401)
async def unauthorized(error):
    task = asyncio.to_thread(render_template, 'unauthorized.html')
    return await task, 401