import re
import traceback

from flask import Blueprint, jsonify, request, session
from flask.ext.login import current_user
from crawler import Crawler
from requests import ConnectionError, URLRequired, RequestException

from db import session_factory
from errors import *
from helpers import get_url, normalize_url
from logger import log
from models.forum import Forum
from models.mod import Mod
from secure import form_key_required
from shared import own_regex

jobs = Blueprint('jobs', __name__)

@jobs.route('/1', methods=['POST'])
@form_key_required
def crawl():
    if 'crawling' in session and session['crawling']:
        return

    session['crawling'] = True

    if 'url' not in request.form or not request.form['url'].strip():
        return jsonify({
            'status': NO_DATA
        })

    url = request.form['url'].strip()
    url = normalize_url(url)

    try:
        test = get_url(url)
        bpath = re.findall(r'\$\.zb\.stat={[^}]+bpath:(\d+)[^}]+};', test.text)

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

        if len(own_test.findall(test.text)) == 0:
            return jsonify({
                'status': NOT_OWNER
            })

        board_key = session['board_key']

        crawler = Crawler(url)
        data = crawler.crawl()

        session['forum'] = dict(
            board_key=board_key,
            bpath=bpath,
            bare_location=url,
            real_location=normalize_url(test.url)
        )

        return jsonify(session['forum'])

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
    finally:
        session['crawling'] = False

@jobs.route('/2', methods=['POST'])
@form_key_required
def add_api_key():
    with session_factory() as sess:
        mod = Mod(api_key=session['board_key'], name=request.form['name'])
        sess.add(mod)

    del session['board_key']

    return jsonify({
        'status': 0
    })

@jobs.route('/3', methods=['POST'])
@form_key_required
def update_mod_keys():
    try:
        key = unicode(request.form['key'])
        keys = current_user.mod_keys.split('\r\n')

        if key in keys:
            keys.remove(key)
        else:
            keys.append(key)

        current_user.mod_keys = '\r\n'.join(keys)

        current_user.save()

        return jsonify({
            'status': 0
        })
    except:
        log('Unknown error occurred:', traceback.format_exc())

        return jsonify({
            'status': UNKNOWN_EXCEPTION
        })

@jobs.route('/4', methods=['POST'])
@form_key_required
def get_mod_info():
    with session_factory() as sess:
        mod = Mod.from_key(request.form['key'])

        if mod is None:
            return jsonify({
                'status': MOD_DOES_NOT_EXIST
            })
        else:
            return jsonify({
                'status': 0,
                'name': mod.name,
                'key': mod.api_key,
                'enabled': mod.enabled and mod.root_enabled
            })

@jobs.route('/5', methods=['POST'])
@form_key_required
def update_board_url():
    url = normalize_url(request.form['url'])
    current_user.real_location = url
    current_user.save()

    return jsonify({
        'url': url
    })
