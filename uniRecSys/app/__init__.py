from flask import Flask
from flask.ext.mongoengine import MongoEngine
from flask.ext.mongorest import MongoRest
from flask.ext.bcrypt import Bcrypt
import os

app = Flask(__name__)
app.config.from_pyfile('../config.py')
if os.environ.get("TESTING"):
    app.config["MONGODB_DB"] = 'testing'
else:
    app.config["MONGODB_DB"] = 'uniRec'
bcrypt = Bcrypt(app)
db = MongoEngine(app)
api = MongoRest(app)

from uniRecSys.app import views, models
