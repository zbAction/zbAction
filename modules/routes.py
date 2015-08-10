import re, uuid

from flask import abort, jsonify, render_template, request, session, url_for
from jinja2.exceptions import TemplateNotFound
from requests import ConnectionError, URLRequired, RequestException
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import bindparam
import traceback

from main import app, bcrypt

from crawler import Crawler
from db import engine, session_factory
from errors import *
from helpers import gen_key_script, get_url, normalize_url
from logger import log
from models.forum import Forum
from models.mod import Mod
from models.user import User
from secure import form_key_required, get_form_key
from shared import own_regex

# Routes

@app.errorhandler(404)
@app.errorhandler(500)
@app.route('/error')
@app.route('/error/<err>')
def oops(err):
    try:
        return render_template('errors/{}.html'.format(err)), err
    except TemplateNotFound:
        return render_template('errors/404.html'), 404

@app.route('/mods/list/<board_key>', methods=['GET'])
def list_mods(board_key):
    try:
        with session_factory() as sess:
            forum = sess.query(Forum.mod_keys).filter(
                Forum.board_key==board_key,
                Forum.enabled==True
            ).one()

            mods = forum.mod_keys.split(' ')

            mods = sess.query(Mod.api_key).filter(
                Mod.api_key.in_(mods),
                Mod.enabled==True,
                Mod.root_enabled==True
            ).all()

            return jsonify({
                'mods': [mod.api_key for mod in mods]
            })
    except NoResultFound:
        return jsonify({})

@app.route('/register', methods=['GET'])
def register():
    session['board_key'] = str(uuid.uuid4())

    return render_template(
        'register.html',
        board_key=session['board_key'],
        gen_key_script=gen_key_script()
    )

@app.route('/finalize', methods=['POST'])
@form_key_required
def finalize():
    if 'password' not in request.form or len(request.form['password'].strip()) == 0:
        return jsonify({
            'status': NO_DATA
        })

    password = bcrypt.generate_password_hash(request.form['password'])

    forum = session['forum']
    forum = Forum(password=password, **forum)
    user_data = session['user_data']

    del session['forum']
    del session['user_data']
    del session['board_key']

    try:
        forum.save()

        users = [
            {
                'access_key': str(uuid.uuid4()),
                'board_key': forum.board_key,
                'uid': user[0],
                'name': user[1]
            }

            for user in user_data
        ]

        engine.execute(User.__table__.insert(), users)
    except:
        log('Unknown error occurred:', traceback.format_exc())

        return jsonify({
            'status': UNKNOWN_EXCEPTION 
        })

    return jsonify({
        'status': 0
    })

@app.route('/registered', methods=['GET'])
def registered():
    return render_template('registered.html', gen_key_script=gen_key_script)

@app.route('/crawl', methods=['POST'])
@form_key_required
def crawl():
    if 'url' not in request.form or not request.form['url'].strip():
        return jsonify({
            'status': NO_DATA
        })

    url = request.form['url'].strip()
    url = normalize_url(url)

    try:
        test = get_url(url).text
        bpath = re.findall(r'\$\.zb\.stat={[^}]+bpath:(\d+)[^}]+};', test)

        if not len(bpath):
            return jsonify({
                'status': NOT_A_BOARD
            })

        bpath = bpath[0].strip()

        if Forum.bpath_exists(bpath):
            return jsonify({
                'status': BOARD_IN_USE
            })

        own_test = re.compile(
            own_regex(session['board_key'])
        )

        if len(own_test.findall(test)) == 0:
            return jsonify({
                'status': NOT_OWNER
            })

        board_key = session['board_key']

        crawler = Crawler(url)
        data = crawler.crawl()

        session['forum'] = dict(board_key=board_key, bpath=bpath, bare_location=url)
        session['user_data'] = data

        return jsonify({
            'status': 0
        })
    except (URLRequired, ConnectionError) as e:
        log('Invalid URL given to crawl:', traceback.format_exc())

        return jsonify({
            'status': INVALID_CRAWL_URL
        })
    except RequestException:
        log('Unknown error occurred:', traceback.format_exc())

        return jsonify({
            'status': UNKNOWN_EXCEPTION
        })

@app.route('/add-api-key')
@form_key_required
def add_api_key():
    with session_factory() as sess:
        mod = Mod(api_key=session['board_key'])
        sess.add(mod)

    del session['board_key']

    return jsonify({
        'status': 0
    })

@app.route('/docs/<category>', methods=['GET'], defaults={'page': 'index'})
@app.route('/docs/<category>/<page>', methods=['GET'])
def docs(category, page):
    try:
        return render_template('docs/{}/{}.html'.format(category, page))
    except TemplateNotFound:
        abort(404)

@app.route('/<int:uid>')
def index(uid):
    return render_template('test.html', uid=uid)