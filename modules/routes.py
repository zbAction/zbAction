import re, textwrap, uuid

from flask import jsonify, render_template, request, session, url_for
from requests import ConnectionError, URLRequired, RequestException
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import bindparam
import traceback

from main import app, bcrypt

from crawler import Crawler
from db import engine, session_factory
from errors import *
from helpers import get_url, normalize_url
from logger import log
from models.forum import Forum
from models.mod import Mod
from models.user import User
from secure import form_key_required, get_form_key
from shared import own_regex

'''
        # Upsert user data
        conn.execute(addresses.insert(), [ 
           {'user_id': 1, 'email_address' : 'jack@yahoo.com'},
           {'user_id': 1, 'email_address' : 'jack@msn.com'},
           {'user_id': 2, 'email_address' : 'www@www.org'},
           {'user_id': 2, 'email_address' : 'wendy@aol.com'},
        ])

from sqlalchemy.sql.expression import bindparam
stmt = addresses.update().\
    where(addresses.c.id == bindparam('_id')).\
    values({
        'user_id': bindparam('user_id'),
        'email_address': bindparam('email_address'),
    })

conn.execute(stmt, [
    {'user_id': 1, 'email_address' : 'jack@yahoo.com', '_id':1},
    {'user_id': 1, 'email_address' : 'jack@msn.com', '_id':2},
    {'user_id': 2, 'email_address' : 'www@www.org', '_id':3},
    {'user_id': 2, 'email_address' : 'wendy@aol.com', '_id':4},
])
'''

# Routes

def gen_key_script():
    key = session['board_key']

    script = '''
    <script>window.__zbAction = {{board_key: '{}'}};</script>
    '''

    script = textwrap.dedent(script).strip().format(key)

    return script

@app.route('/mods/list/<board_key>')
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

@app.route('/register')
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

    print session

    forum = session['forum']
    forum = Forum(password=password, **forum)
    user_data = session['user_data']

    session.clear()

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

    return jsonify(dict(good='Good'))

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

        '''
        if len(own_test.findall(test)) == 0:
            return jsonify({
                'status': NOT_OWNER
            })
        '''

        board_key = session['board_key']

        crawler = Crawler(url)
        data = crawler.crawl()

        session['forum'] = dict(board_key=board_key, bpath=bpath, bare_location=url)
        print session['forum']
        session['user_data'] = data
        print session['forum']

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

@app.route('/<uid>')
def index(uid):
    return render_template('test.html', uid=uid)