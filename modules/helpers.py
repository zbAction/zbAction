from datetime import datetime, timedelta
import textwrap
import traceback
import requests

from flask import session

from db import session_factory
from models.action import Action
from models.user import User
from secrets import secrets

def get_url(url):
    headers = {'user-agent': 'zbaBot/1.0'}
    resp = requests.get(url, headers=headers)

    return resp

def check_server():
    try:
        # 50ms timeout
        requests.get(secrets.websocket_url, timeout=0.05)
        return True
    except:
        return False

def serialize(var):
    if isinstance(var, User):
        return var.to_json()

    if isinstance(var, Action):
        return var.to_json()

    if isinstance(var, object):
        return var.__dict__
    else:
        return var

def within_one_week(timestamp):
    now = datetime.utcnow()
    week = timedelta(weeks=1)

    return timestamp + week >= now

def gen_key_script():
    key = session['board_key']

    script = '''
    <script>window.__zbAction = {{board_key: '{}'}};</script>
    '''

    script = textwrap.dedent(script).strip().format(key)

    return script

def get_unread(user):
    with session_factory() as session:
        actions = session.query(
            Action
        ).filter(
            Action.receiver==user.access_key,
            Action.seen==False
        ).all()

        session.expunge_all()

        return actions

def normalize_url(url):
    if url.find('http://') != 0:
        url = 'http://' + url

    if url[-1] != '/':
        url += '/'

    return url
