#!/usr/bin/python3

from flask import Flask, Response, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from db_models import db, User, Manuscript, Page, Transcription, TokenCache
from config import Config
from flask_migrate import Migrate
import commands

app = Flask(__name__, instance_relative_config=True)
app.config.from_object(Config)
app.config.from_pyfile('override.cfg')

CORS(app)
db.init_app(app)
migrate = Migrate(app, db)
commands.init_app(app)

@app.route('/')
def home():
    return 'Endpoint'


if __name__ == "__main__":
    app.run(debug=True) # disable on prod