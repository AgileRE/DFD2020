from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '4b5402378ffe97929b29f1b25a178254'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'warning'

project_session = {'project_name':'', 'curr_route':'', 'path': ''}

path = os.path.join(app.root_path, "user_project")
if not os.path.exists(path):
    user_project_path = os.path.join(app.root_path, "user_project")
    os.mkdir(user_project_path)

if not os.path.exists(os.path.join(app.root_path, 'site.db')):
    db.create_all()

from DFD2GUI import routes