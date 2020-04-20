#!/usr/bin/python3

from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy, inspect
from sqlalchemy import func
import requests

from db_models import db, User, Manuscript, Page, Transcription, TokenCache
from config import Config
from flask_migrate import Migrate
import commands

app = Flask(__name__, instance_relative_config=True)
app.config.from_object(Config)
try:
    app.config.from_pyfile('override.cfg')
except FileNotFoundError:
    pass

CORS(app)
db.init_app(app)
migrate = Migrate(app, db)
commands.init_app(app)

ENDPOINT = 'https://openidconnect.googleapis.com/v1/userinfo'

def get_user_from_token(token: str) -> str:
    # Check the token cache first:
    if not token:
        return None
    cached = db.session.query(TokenCache).filter(TokenCache.token == token).first()
    if cached:
        print('Loading from cache')
        return cached.email

    print('Triggered a check')
    t1 = time.perf_counter_ns()
    user_data = requests.get(ENDPOINT, {'access_token': token}).json()
    # user = oauth.google.authorize_access_token(token)
    email = user_data.get('email')
    if email:
        exists = db.session.query(User).filter(User.email == email).first()
        if not exists:
            user = User(email=email, first_name=user_data.get('given_name'), last_name=user_data.get('family_name'))
            db.session.add(user)
            db.session.commit()
            print(f'Added user {user}')
        # Wipe the user from cache
        db.session.query(TokenCache).filter(TokenCache.email == email).delete()
        update_cache = TokenCache(token=token, email=email, token_provider='google')
        db.session.add(update_cache)
        db.session.commit()

        t2 = time.perf_counter_ns()
        print(t2 - t1)
        return email
    return None

def get_user() -> str:
    return request.values.get("user_email") or get_user_from_token(request.values.get('token'))

@app.route('/chktoken', methods=['GET'])
def check_token():
    token = request.values.get('token')
    user = get_user_from_token(token)
    return user


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


@app.route("/pending", methods=["GET"])
def get_pending_manuscripts():
    """ List of manuscripts waiting for the user’s transcriptions, ordered by priority. """
    user_email = get_user()

    # TODO: more advanced ordering mechanism than this
    # LIMIT_MSS = 5

    user_pages = db.session.query(Transcription.page_id).filter(Transcription.user_email == user_email)
    mss = db.session.query(Manuscript)
    payload = {'manuscript': []}
    for ms in mss:
        pg_ms = db.session.query(Page).filter(Page.manuscript_id == ms.id).filter(Page.id.notin_(user_pages))
        l = [object_as_dict(p) for p in pg_ms]
        if l:
            d = object_as_dict(ms)
            d['pages'] = l
            payload['manuscript'].append(d)

    return jsonify(payload)


@app.route("/featured", methods=["GET"])
def get_featured_manuscripts():
    """ List of 3 featured manuscripts, for the carousel view. """
    LIMIT_MSS = 3

    # TODO: curated system for what's featured
    nocover_pages = db.session.query(Page.manuscript_id).filter(Page.page_name != 'Front Cover')
    mss = db.session.query(Manuscript).filter(Manuscript.id.in_(nocover_pages)).order_by(func.random()).limit(LIMIT_MSS)
    payload = {'manuscript': []}
    for ms in mss:
        # TODO: get the key page for display
        pg_ms = db.session.query(Page).filter(Page.manuscript_id == ms.id).filter(
            Page.page_name != 'Front Cover').first()
        d = object_as_dict(ms)
        d['page'] = object_as_dict(pg_ms)
        payload['manuscript'].append(d)

    return jsonify(payload)


@app.route("/pending/<int:page_id>", methods=['PUT'])
def start_transcription(page_id):
    """ Note: the backend creates the transcription record prior to returning it to 
    the user. Record has a start_date with no save_date, a suggestion_id (if there 
    is one) and no text. Partial is set to true at this point. If there is already
    a partial record for this user and this page - return it instead of creating a 
    new record. """
    user_email = get_user()
    exists = (
        db.session.query(Transcription)
        .filter(Transcription.page_id == page_id)
        .filter(Transcription.user_email == user_email)
        .filter(Transcription.partial == True)
        .first()
    )
    if exists:
        payload = object_as_dict(exists)
        initial_text = exists.initial_transcription.transcription if exists.initial_transcription else None
        payload['suggestion'] = {'id': exists.initial_transcription_id, 'text': initial_text}
        payload['page'] = object_as_dict(exists.page)
        payload['manuscript'] = object_as_dict(exists.page.manuscript)
        return jsonify(payload)

    initial_id = None
    suggestion = None
    initial = get_transcription_id_base(page_id)
    if initial:
        initial_id = initial.id
        suggestion = initial.transcription
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
    payload['page'] = object_as_dict(new_tr.page)
    payload['manuscript'] = object_as_dict(new_tr.page.manuscript)
    return jsonify(payload)


@app.route('/transcription/<int:transcription_id>', methods=['PUT'])
def save_new_transcription(transcription_id):
    ''' The frontend uses this endpoint to save a new transcription to the database. 
    Notes: the backend first checks that the transcription belongs to the user 
    (returning a 404 if not), and that it is partial. The backend updates the text,
    sets partial to false. '''
    user_email = get_user()
    transcription = db.session.query(Transcription).filter(Transcription.id == transcription_id).first()
    if transcription.user_email != user_email or transcription.partial != True:
        return jsonify(), 404

    transcription.transcription = request.values.get('text')
    transcription.partial = False
    db.session.commit()
    return jsonify(success=True)


@app.route('/page/<int:page_id>', methods=['GET'])
def get_page(page_id):
    page = db.session.query(Page).filter(Page.id == page_id).first()
    payload = object_as_dict(page)
    payload['manuscript'] = object_as_dict(page.manuscript)
    return jsonify(payload)


@app.route('/manuscript/<int:manuscript_id>', methods=['GET'])
def get_manuscript(manuscript_id):
    user_email = get_user()
    manuscript = db.session.query(Manuscript).filter(Manuscript.id == manuscript_id).first()
    user_pages_complete = db.session.query(Transcription.page_id).filter(
        Transcription.user_email == user_email).filter(Transcription.partial == False).all()
    user_pages_partial = db.session.query(Transcription.page_id).filter(
        Transcription.user_email == user_email).filter(Transcription.partial == True).all()
    pages = db.session.query(Page).filter(Page.manuscript_id == manuscript_id)

    payload = object_as_dict(manuscript)
    user_pages_complete = [x[0] for x in user_pages_complete]
    user_pages_partial = [x[0] for x in user_pages_partial]
    payload['pages'] = []
    print(user_pages_complete, user_pages_partial)
    for page in pages:
        # status = 'none'
        if page.id in user_pages_complete:
            status = 'complete'
        elif page.id in user_pages_partial:
            status = 'partial'
        # TODO: add not required = enough other users have done it
        else:
            status = 'none'
        pg = object_as_dict(page)
        pg['status'] = status
        payload['pages'].append(pg)
    return jsonify(payload)


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
    app.run(debug=True, port=3000)  # disable on prod
