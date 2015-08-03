import os, uuid

from flask import jsonify, render_template, request, session, url_for
from requests import URLRequired, RequestException
from sqlalchemy.orm.exc import NoResultFound
import traceback

from main import app

from crawler import Crawler
from db import session_factory
from helpers import get_url
from logger import log
from models.forum import Forum
from models.mod import Mod

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
    return render_template('register.html')

@app.route('/crawl', methods=['POST'])
def crawl():
    if 'url' not in request.form or not request.form['url'].strip():
        return jsonify({
            'status': 3
        })

    url = request.form['url'].strip()

    # This is needed so we urllib2 can actually
    # open it. The final slash is to standardize
    # all of them.

    if url.find('http://') != 0:
        url = 'http://' + url

    if url[-1] != '/':
        url += '/'

    try:
        get_url(url)

        board_key = int(uuid.uuid4())
        session['board_key'] = board_key

        crawler = Crawler(url)
        data = crawler.crawl()

        return str(len(data))
    except URLRequired:
        log('Invalid URL given to crawl:', traceback.format_exc())

        return jsonify({
            'status': 1
        })
    except RequestException:
        log('Unknown error occurred:', traceback.format_exc())

        return jsonify({
            'status': 2
        })

@app.route('/check-in-use', methods=['POST'])
def check_in_use():
    if 'url' not in request.form or not len(request.form['url'].strip()):
        return jsonify({
            'status': 2
        })

    with session_factory() as sess:
        try:
            sess.query(Forum.bare_url).filter(
                forum.bare_url==request.form['url']
            ).one()

            return jsonify({
                'status': 1
            })
        except NoResultFound:
            return jsonify({
                'status': 0
            })


@app.route('/<uid>')
def index(uid):
    return render_template('test.html', uid=uid)

'''
Utilities
'''

def cache_bust(ep, **kwargs):
    if ep == 'static' and 'filename' in kwargs:
        file = kwargs['filename']
        path = os.path.join(app.root_path, 'static', file)
        lm = int(os.stat(path).st_mtime)

        kwargs['m'] = lm

    return url_for(ep, **kwargs)

@app.context_processor
def injections():
    return {
        'url_for': cache_bust
    }