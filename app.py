#!/usr/bin/python3

from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy, inspect

from db_models import db, User, Manuscript, Page, Transcription, TokenCache
from config import Config
from flask_migrate import Migrate
import commands

app = Flask(__name__)
app.config.from_object(Config)

CORS(app)
db.init_app(app)
migrate = Migrate(app, db)
commands.init_app(app)

# TODO: maybe switch to @dataclass for serializing in 3.8?


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}


def get_transcription_id_base(page_id: int) -> int:
    """ Get the current transcription id that should be based off of """
    return (
        db.session.query(Transcription)
        .filter(Transcription.page_id == page_id)
        .filter(Transcription.partial == False)
        .order_by(Transcription.start_time.desc())
        .first()
    )


@app.route("/")
def home():
    return "Endpoint"


@app.route("/pending", methods=["GET"])
def get_pending_manuscripts():
    """ List of manuscripts waiting for the user’s transcriptions, ordered by priority. """
    user_email = request.values.get('user_email') # TODO: swap this for the tokens

    # TODO: more advanced ordering mechanism than this
    LIMIT_MSS = 5

    user_pages = db.session.query(Transcription.page_id).filter(Transcription.user_email == user_email)
    mss = db.session.query(Manuscript)
    payload = {'manuscript': []}
    for ms in mss:
        pg_ms = db.session.query(Page).filter(Page.manuscript_id == ms.id).filter(Page.id.notin_(user_pages))
        l = [object_as_dict(p) for p in pg_ms]
        d = object_as_dict(ms)
        d['pages'] = l
        payload['manuscript'].append(d)

    return jsonify(payload)


@app.route("/pending/<int:page_id>", methods=['PUT'])
def start_transcription(page_id):
    """ Note: the backend creates the transcription record prior to returning it to 
    the user. Record has a start_date with no save_date, a suggestion_id (if there 
    is one) and no text. Partial is set to true at this point. If there is already
    a partial record for this user and this page - return it instead of creating a 
    new record. """
    user_email = request.args.get("user_email")  # TODO: swap this for the tokens

    exists = (
        db.session.query(Transcription)
        .filter(Transcription.page_id == page_id)
        .filter(Transcription.user_email == user_email)
        .filter(Transcription.partial == True)
        .first()
    )
    if exists:
        return jsonify(object_as_dict(exists))

    initial_id = None
    suggestion = None
    initial = get_transcription_id_base(page_id)
    if initial:
        initial_id = initial.id
        suggestion = initial.text
    new_tr = Transcription(
        page_id=page_id,
        user_email=user_email,
        partial=True,
        transcription="",
        initial_transcription_id=initial_id,
    )

    db.session.add(new_tr)
    db.session.commit()

    payload = object_as_dict(new_tr)
    payload['suggestion'] = {'id': initial_id, 'text': suggestion}
    return jsonify(payload)


@app.route('/transcription/<int:transcription_id>', methods=['PUT'])
def save_new_transcription(transcription_id):
    ''' The frontend uses this endpoint to save a new transcription to the database. 
    Notes: the backend first checks that the transcription belongs to the user 
    (returning a 404 if not), and that it is partial. The backend updates the text,
    sets partial to false. '''
    user_email = request.values.get("user_email")  # TODO: swap this for the tokens
    transcription = db.session.query(Transcription).filter(Transcription.id == transcription_id).first()
    if transcription.user_email != user_email or transcription.partial != True:
        return jsonify(), 404

    transcription.transcription = request.values.get('text')
    transcription.partial = False
    db.session.commit()
    return jsonify(success=True)


@app.route("/manuscripts")
def get_manuscripts():
    ''' NOTE: this endpoint isn't in the spec, here for debugging '''
    mss = db.session.query(Manuscript).all()
    return jsonify([object_as_dict(m) for m in mss])


@app.route("/pages")
def get_pages():
    ''' NOTE: this endpoint isn't in the spec, here for debugging '''
    pgs = db.session.query(Page).all()
    return jsonify([object_as_dict(p) for p in pgs])


if __name__ == "__main__":
    app.run(debug=True)  # disable on prod
