

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from flask_user import login_required, UserManager, UserMixin, current_user

class ConfigClass(object):
    """ Flask application config """

    # Flask settings
    # As of now, we don't need sessions or to sign anything. If we ever do, we'll generate a new one and store it somewhere else.
    SECRET_KEY = "6d08b92e3a5860d3daf1ccb98caeeb5c9d8ef736210dcb74cfeff819baf90f0f"
    # 32 bytes (256 bits), produced with secrets.token_hex (Py3.6)

    # Flask-SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = "sqlite:///plague-transcriptions.db"  # File-based SQL database for now, will prob change for later
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Avoids SQLAlchemy warning

# Create Flask app load app.config
app = Flask(__name__)
app.config.from_object(__name__ + ".ConfigClass")

# Initialize Flask-SQLAlchemy
db = SQLAlchemy(app)


class User(db.Model): # Do we need Flask-User integration later?
    __tablename__ = "users"
    email = db.Column(db.String(255), primary_key=True)
    # User fields
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))


class Manuscript(db.Model):
    ''' Records per manuscript
    '''
    __tablename__ = "manuscripts"
    id = db.Column(db.Integer, primary_key=True)
    heb_name = db.Column(db.String(255))
    eng_name = db.Column(db.String(255))
    estimated_date = db.Column(db.String(50))
    shelf_no = db.Column(db.String(100))
    catalog_no = db.Column(db.String(100))
    external_url = db.Column(db.String(255)) # for ktiv where applicable
    iiif_manifest_url = db.Column(db.String(255))
    license = db.Column(db.Text)
    notes = db.Column(db.Text)

class Page(db.Model):
    ''' Manuscript pages, the main transliteration unit
    '''
    __tablename__ = 'pages'
    id = db.Column(db.Integer, primary_key=True)
    page_name = db.Column(db.String(255))
    page_number = db.Column(db.Integer)
    iiif_url = db.Column(db.String(255))
    page_width = db.Column(db.Integer)
    page_height = db.Column(db.Integer)
    dpi = db.Column(db.Integer)

class TokenCache(db.Model): # NOTE: this may be moved to some sort of cache system?
    __tablename__ = 'tokencache'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(255))
    token_provider = db.Column(db.String(255))
    email = db.Column(db.String(255))

class Transcription(db.Model):
    __tablename__ = 'transcriptions'
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(255), db.ForeignKey("users.email"))
    partial = db.Column(db.Boolean, server_default='1')
    inital_transcription_id = db.Column(db.Integer, db.ForeignKey('transcriptions.id'))
    transcription = db.Column(db.Text)
    start_time = db.Column(db.TIMESTAMP, server_default=db.func.now())
    save_time = db.Column(db.TIMESTAMP, onupdate=db.func.current_timestamp())

    # added to
    initial_transcription = db.relationship('Transcription', backref="children", remote_side="Transcription.id")

db.create_all()