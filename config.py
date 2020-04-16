#!/usr/bin/python3

class Config(object):
    """ Flask application config """

    # Flask settings
    # As of now, we don't need sessions or to sign anything. If we ever do, we'll generate a new one and store it somewhere else.
    SECRET_KEY = "6d08b92e3a5860d3daf1ccb98caeeb5c9d8ef736210dcb74cfeff819baf90f0f"
    # 32 bytes (256 bits), produced with secrets.token_hex (Py3.6)

    # Flask-SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = "sqlite:///plague-transcriptions.db"  # File-based SQL database for now, will prob change for later
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Avoids SQLAlchemy warning
    
    # Since we've got lots of Hebrew JSON
    JSON_AS_ASCII = False

