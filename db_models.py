#!/usr/bin/python3

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from flask_user import login_required, UserManager, UserMixin, current_user

# Initialize Flask-SQLAlchemy empty, we'll init_app this later 
db = SQLAlchemy()


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
    heb_name = db.Column(db.String(255), unique=True)
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
    iiif_url = db.Column(db.String(255), unique=True)
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

# db.create_all()