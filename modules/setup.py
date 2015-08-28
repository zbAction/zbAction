import os

from flask import request, session, url_for

from main import app, loader, login_manager

from helpers import check_server
from models.forum import Forum
from models.mod import Mod
from secure import get_form_key

login_manager.login_message_category = 'red'
login_manager.login_view = 'meta.login'
login_manager.refresh_view = 'meta.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(userid):
    return Forum.from_id(int(userid))

def cache_bust(ep, **kwargs):
    if ep == 'static' and 'filename' in kwargs:
        file = kwargs['filename']
        path = os.path.join(app.root_path, 'static', file)
        lm = int(os.stat(path).st_mtime)

        kwargs['m'] = lm

    return url_for(ep, **kwargs)

'''
@app.before_first_request
def setup():
    session.pop('form_key', None)
    session['form_key'] = get_form_key()
'''

@app.before_request
def setup2():
    get_form_key()

def include_source(f):
    return open(os.path.join(app.root_path, f)).read()

@app.context_processor
def injections():
    server_online = check_server()

    return {
        'url_for': cache_bust,
        'get_form_key': get_form_key,
        'include_source': include_source,
        'server_online': server_online
    }
