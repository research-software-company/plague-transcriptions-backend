#!/usr/bin/python3
from os import environ

class Config(object):
    """ Flask application config """

    # Flask settings
    # In production, we will override the secret key and database URI from the environment
    SECRET_KEY = environ.get("SECRET_KEY") or "6d08b92e3a5860d3daf1ccb98caeeb5c9d8ef736210dcb74cfeff819baf90f0f"
    # 32 bytes (256 bits), produced with secrets.token_hex (Py3.6)

    # Flask-SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = environ.get("SQLALCHEMY_DATABASE_URI") or "sqlite:///plague-transcriptions.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Avoids SQLAlchemy warning
    
    # Since we've got lots of Hebrew JSON
    JSON_AS_ASCII = False


