import re

from flask import Blueprint, jsonify, request, session
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

jobs = Blueprint('jobs', __name__, url_prefix='/jobs')

@jobs.route('/crawl', methods=['POST'])
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

@jobs.route('/add-api-key')
@form_key_required
def add_api_key():
    with session_factory() as sess:
        mod = Mod(api_key=session['board_key'])
        sess.add(mod)

    del session['board_key']

    return jsonify({
        'status': 0
    })
