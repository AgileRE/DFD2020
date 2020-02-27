from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = '4b5402378ffe97929b29f1b25a178254'

from DFD2GUI import routes